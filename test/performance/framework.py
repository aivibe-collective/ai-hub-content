"""
Performance testing framework for the Agentic AI Content Creation System.
"""

import time
import statistics
import json
import os
import logging
import datetime
import abc
import matplotlib.pyplot as plt
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test/performance/logs/performance.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('performance')

class PerformanceTest(abc.ABC):
    """Base class for performance tests."""
    
    def __init__(self, name, description, category):
        """
        Initialize the performance test.
        
        Args:
            name (str): Name of the test.
            description (str): Description of the test.
            category (str): Category of the test (load, stress, endurance, scalability, api_response).
        """
        self.name = name
        self.description = description
        self.category = category
        self.start_time = None
        self.end_time = None
        self.results = {
            'name': name,
            'description': description,
            'category': category,
            'metrics': {},
            'start_time': None,
            'end_time': None,
            'duration': None,
            'status': 'not_run',
            'error': None
        }
        self.report_dir = f"test/performance/reports/{category}"
        os.makedirs(self.report_dir, exist_ok=True)
    
    def execute(self):
        """Execute the performance test."""
        logger.info(f"Starting performance test: {self.name}")
        self.start_time = time.time()
        self.results['start_time'] = datetime.datetime.now().isoformat()
        
        try:
            self.setup()
            self.run()
            self.results['status'] = 'success'
        except Exception as e:
            logger.error(f"Error in performance test {self.name}: {str(e)}")
            self.results['status'] = 'error'
            self.results['error'] = str(e)
        finally:
            self.cleanup()
            self.end_time = time.time()
            self.results['end_time'] = datetime.datetime.now().isoformat()
            self.results['duration'] = self.end_time - self.start_time
            self.generate_report()
            logger.info(f"Completed performance test: {self.name}")
        
        return self.results
    
    @abc.abstractmethod
    def setup(self):
        """Set up the performance test."""
        pass
    
    @abc.abstractmethod
    def run(self):
        """Run the performance test."""
        pass
    
    @abc.abstractmethod
    def cleanup(self):
        """Clean up after the performance test."""
        pass
    
    def generate_report(self):
        """Generate a report for the performance test."""
        # Save results to JSON file
        report_file = f"{self.report_dir}/{self.name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Generate charts if metrics are available
        if self.results['metrics']:
            self.generate_charts()
    
    def generate_charts(self):
        """Generate charts for the performance test metrics."""
        charts_dir = f"{self.report_dir}/charts"
        os.makedirs(charts_dir, exist_ok=True)
        
        for metric_name, metric_data in self.results['metrics'].items():
            if isinstance(metric_data, list) and len(metric_data) > 1:
                plt.figure(figsize=(10, 6))
                plt.plot(metric_data)
                plt.title(f"{self.name} - {metric_name}")
                plt.xlabel("Request Number")
                plt.ylabel(metric_name)
                plt.grid(True)
                plt.savefig(f"{charts_dir}/{self.name}_{metric_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                plt.close()
            elif isinstance(metric_data, dict) and 'values' in metric_data and len(metric_data['values']) > 1:
                plt.figure(figsize=(10, 6))
                plt.plot(metric_data['values'])
                plt.title(f"{self.name} - {metric_name}")
                plt.xlabel("Request Number")
                plt.ylabel(metric_name)
                plt.grid(True)
                plt.savefig(f"{charts_dir}/{self.name}_{metric_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                plt.close()

class LoadTest(PerformanceTest):
    """Base class for load tests."""
    
    def __init__(self, name, description, endpoint, num_users=10, requests_per_user=10, ramp_up_time=5):
        """
        Initialize the load test.
        
        Args:
            name (str): Name of the test.
            description (str): Description of the test.
            endpoint (str): API endpoint to test.
            num_users (int): Number of concurrent users.
            requests_per_user (int): Number of requests per user.
            ramp_up_time (int): Time in seconds to ramp up to full load.
        """
        super().__init__(name, description, 'load')
        self.endpoint = endpoint
        self.num_users = num_users
        self.requests_per_user = requests_per_user
        self.ramp_up_time = ramp_up_time
        self.response_times = []
        self.error_count = 0
        self.success_count = 0
    
    def setup(self):
        """Set up the load test."""
        logger.info(f"Setting up load test: {self.name}")
        logger.info(f"Endpoint: {self.endpoint}")
        logger.info(f"Number of users: {self.num_users}")
        logger.info(f"Requests per user: {self.requests_per_user}")
        logger.info(f"Ramp-up time: {self.ramp_up_time} seconds")
        
        # Initialize metrics
        self.results['metrics'] = {
            'response_times': [],
            'throughput': 0,
            'error_rate': 0,
            'cpu_utilization': [],
            'memory_utilization': []
        }
    
    def run(self):
        """Run the load test."""
        logger.info(f"Running load test: {self.name}")
        
        # Calculate delay between user starts
        if self.num_users > 1:
            delay_between_users = self.ramp_up_time / (self.num_users - 1)
        else:
            delay_between_users = 0
        
        # Create a thread pool
        with ThreadPoolExecutor(max_workers=self.num_users) as executor:
            # Submit tasks for each user
            futures = []
            for user_id in range(self.num_users):
                # Delay start based on user ID
                start_delay = user_id * delay_between_users
                futures.append(executor.submit(self.user_task, user_id, start_delay))
            
            # Monitor system resources during test
            self.monitor_resources()
            
            # Wait for all tasks to complete
            for future in futures:
                future.result()
        
        # Calculate metrics
        self.calculate_metrics()
    
    def user_task(self, user_id, start_delay):
        """
        Task for a single user.
        
        Args:
            user_id (int): User ID.
            start_delay (float): Delay in seconds before starting.
        """
        logger.info(f"User {user_id} starting after {start_delay:.2f} seconds")
        time.sleep(start_delay)
        
        for i in range(self.requests_per_user):
            try:
                start_time = time.time()
                response = self.make_request()
                end_time = time.time()
                
                response_time = end_time - start_time
                self.response_times.append(response_time)
                
                if response.status_code >= 200 and response.status_code < 300:
                    self.success_count += 1
                else:
                    self.error_count += 1
                    logger.warning(f"User {user_id}, Request {i}: Error {response.status_code}")
                
                logger.info(f"User {user_id}, Request {i}: Response time {response_time:.3f} seconds")
            except Exception as e:
                self.error_count += 1
                logger.error(f"User {user_id}, Request {i}: Exception {str(e)}")
    
    def make_request(self):
        """
        Make a request to the API endpoint.
        
        Returns:
            requests.Response: Response from the API.
        """
        return requests.get(self.endpoint)
    
    def monitor_resources(self):
        """Monitor system resources during the test."""
        # Start monitoring in a separate thread
        def _monitor():
            while time.time() < self.end_time:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                
                self.results['metrics']['cpu_utilization'].append(cpu_percent)
                self.results['metrics']['memory_utilization'].append(memory_percent)
                
                time.sleep(1)
        
        # Set end time for monitoring
        self.end_time = time.time() + self.ramp_up_time + 10  # Add buffer
        
        # Start monitoring in a separate thread
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(_monitor)
    
    def calculate_metrics(self):
        """Calculate performance metrics."""
        # Response times
        self.results['metrics']['response_times'] = self.response_times
        
        if self.response_times:
            self.results['metrics']['min_response_time'] = min(self.response_times)
            self.results['metrics']['max_response_time'] = max(self.response_times)
            self.results['metrics']['avg_response_time'] = statistics.mean(self.response_times)
            self.results['metrics']['median_response_time'] = statistics.median(self.response_times)
            
            # Calculate percentiles
            self.results['metrics']['p90_response_time'] = np.percentile(self.response_times, 90)
            self.results['metrics']['p95_response_time'] = np.percentile(self.response_times, 95)
            self.results['metrics']['p99_response_time'] = np.percentile(self.response_times, 99)
        
        # Throughput
        total_requests = self.success_count + self.error_count
        total_time = self.end_time - self.start_time
        self.results['metrics']['throughput'] = total_requests / total_time if total_time > 0 else 0
        
        # Error rate
        self.results['metrics']['error_rate'] = (self.error_count / total_requests) * 100 if total_requests > 0 else 0
        
        # Resource utilization
        if self.results['metrics']['cpu_utilization']:
            self.results['metrics']['avg_cpu_utilization'] = statistics.mean(self.results['metrics']['cpu_utilization'])
            self.results['metrics']['max_cpu_utilization'] = max(self.results['metrics']['cpu_utilization'])
        
        if self.results['metrics']['memory_utilization']:
            self.results['metrics']['avg_memory_utilization'] = statistics.mean(self.results['metrics']['memory_utilization'])
            self.results['metrics']['max_memory_utilization'] = max(self.results['metrics']['memory_utilization'])
    
    def cleanup(self):
        """Clean up after the load test."""
        logger.info(f"Cleaning up load test: {self.name}")

class StressTest(LoadTest):
    """Base class for stress tests."""
    
    def __init__(self, name, description, endpoint, start_users=10, max_users=100, step_size=10, step_duration=60):
        """
        Initialize the stress test.
        
        Args:
            name (str): Name of the test.
            description (str): Description of the test.
            endpoint (str): API endpoint to test.
            start_users (int): Initial number of concurrent users.
            max_users (int): Maximum number of concurrent users.
            step_size (int): Number of users to add in each step.
            step_duration (int): Duration of each step in seconds.
        """
        super().__init__(name, description, endpoint, num_users=start_users)
        self.category = 'stress'
        self.start_users = start_users
        self.max_users = max_users
        self.step_size = step_size
        self.step_duration = step_duration
        self.breaking_point = None
    
    def run(self):
        """Run the stress test."""
        logger.info(f"Running stress test: {self.name}")
        
        # Initialize metrics for each step
        self.results['metrics'] = {
            'steps': [],
            'breaking_point': None
        }
        
        current_users = self.start_users
        step = 1
        
        while current_users <= self.max_users:
            logger.info(f"Step {step}: Testing with {current_users} users")
            
            # Create a load test for this step
            load_test = LoadTest(
                f"{self.name}_step_{step}",
                f"Step {step} of stress test {self.name} with {current_users} users",
                self.endpoint,
                num_users=current_users,
                requests_per_user=10,
                ramp_up_time=5
            )
            
            # Run the load test
            load_test.execute()
            
            # Add step results to metrics
            step_results = {
                'users': current_users,
                'response_times': load_test.results['metrics'].get('response_times', []),
                'avg_response_time': load_test.results['metrics'].get('avg_response_time', 0),
                'p95_response_time': load_test.results['metrics'].get('p95_response_time', 0),
                'throughput': load_test.results['metrics'].get('throughput', 0),
                'error_rate': load_test.results['metrics'].get('error_rate', 0),
                'avg_cpu_utilization': load_test.results['metrics'].get('avg_cpu_utilization', 0),
                'avg_memory_utilization': load_test.results['metrics'].get('avg_memory_utilization', 0)
            }
            
            self.results['metrics']['steps'].append(step_results)
            
            # Check if we've reached the breaking point
            if step_results['error_rate'] > 5 or step_results['p95_response_time'] > 5:
                logger.info(f"Breaking point reached at {current_users} users")
                self.breaking_point = current_users
                self.results['metrics']['breaking_point'] = current_users
                break
            
            # Increment users for next step
            current_users += self.step_size
            step += 1
            
            # Wait between steps
            time.sleep(5)
    
    def cleanup(self):
        """Clean up after the stress test."""
        logger.info(f"Cleaning up stress test: {self.name}")
        
        # Generate summary charts
        self.generate_summary_charts()
    
    def generate_summary_charts(self):
        """Generate summary charts for the stress test."""
        if not self.results['metrics']['steps']:
            return
        
        charts_dir = f"{self.report_dir}/charts"
        os.makedirs(charts_dir, exist_ok=True)
        
        # Extract data for charts
        users = [step['users'] for step in self.results['metrics']['steps']]
        avg_response_times = [step['avg_response_time'] for step in self.results['metrics']['steps']]
        p95_response_times = [step['p95_response_time'] for step in self.results['metrics']['steps']]
        throughputs = [step['throughput'] for step in self.results['metrics']['steps']]
        error_rates = [step['error_rate'] for step in self.results['metrics']['steps']]
        
        # Response time chart
        plt.figure(figsize=(10, 6))
        plt.plot(users, avg_response_times, label='Average')
        plt.plot(users, p95_response_times, label='95th Percentile')
        plt.title(f"{self.name} - Response Time vs Users")
        plt.xlabel("Number of Users")
        plt.ylabel("Response Time (seconds)")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"{charts_dir}/{self.name}_response_time_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.close()
        
        # Throughput chart
        plt.figure(figsize=(10, 6))
        plt.plot(users, throughputs)
        plt.title(f"{self.name} - Throughput vs Users")
        plt.xlabel("Number of Users")
        plt.ylabel("Throughput (requests/second)")
        plt.grid(True)
        plt.savefig(f"{charts_dir}/{self.name}_throughput_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.close()
        
        # Error rate chart
        plt.figure(figsize=(10, 6))
        plt.plot(users, error_rates)
        plt.title(f"{self.name} - Error Rate vs Users")
        plt.xlabel("Number of Users")
        plt.ylabel("Error Rate (%)")
        plt.grid(True)
        plt.savefig(f"{charts_dir}/{self.name}_error_rate_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.close()

class EnduranceTest(LoadTest):
    """Base class for endurance tests."""
    
    def __init__(self, name, description, endpoint, num_users=10, duration=3600, sampling_interval=60):
        """
        Initialize the endurance test.
        
        Args:
            name (str): Name of the test.
            description (str): Description of the test.
            endpoint (str): API endpoint to test.
            num_users (int): Number of concurrent users.
            duration (int): Test duration in seconds.
            sampling_interval (int): Interval in seconds between metric samples.
        """
        super().__init__(name, description, endpoint, num_users=num_users)
        self.category = 'endurance'
        self.duration = duration
        self.sampling_interval = sampling_interval
        self.samples = []
    
    def run(self):
        """Run the endurance test."""
        logger.info(f"Running endurance test: {self.name}")
        
        # Initialize metrics
        self.results['metrics'] = {
            'samples': [],
            'avg_response_time_trend': [],
            'throughput_trend': [],
            'error_rate_trend': [],
            'cpu_utilization_trend': [],
            'memory_utilization_trend': []
        }
        
        # Calculate number of samples
        num_samples = self.duration // self.sampling_interval
        
        # Run test for specified duration
        end_time = time.time() + self.duration
        sample_num = 1
        
        while time.time() < end_time and sample_num <= num_samples:
            logger.info(f"Sample {sample_num}/{num_samples}")
            
            # Create a load test for this sample
            load_test = LoadTest(
                f"{self.name}_sample_{sample_num}",
                f"Sample {sample_num} of endurance test {self.name}",
                self.endpoint,
                num_users=self.num_users,
                requests_per_user=5,
                ramp_up_time=2
            )
            
            # Run the load test
            load_test.execute()
            
            # Add sample results to metrics
            sample_results = {
                'sample_num': sample_num,
                'timestamp': time.time(),
                'avg_response_time': load_test.results['metrics'].get('avg_response_time', 0),
                'p95_response_time': load_test.results['metrics'].get('p95_response_time', 0),
                'throughput': load_test.results['metrics'].get('throughput', 0),
                'error_rate': load_test.results['metrics'].get('error_rate', 0),
                'avg_cpu_utilization': load_test.results['metrics'].get('avg_cpu_utilization', 0),
                'avg_memory_utilization': load_test.results['metrics'].get('avg_memory_utilization', 0)
            }
            
            self.results['metrics']['samples'].append(sample_results)
            
            # Update trend metrics
            self.results['metrics']['avg_response_time_trend'].append(sample_results['avg_response_time'])
            self.results['metrics']['throughput_trend'].append(sample_results['throughput'])
            self.results['metrics']['error_rate_trend'].append(sample_results['error_rate'])
            self.results['metrics']['cpu_utilization_trend'].append(sample_results['avg_cpu_utilization'])
            self.results['metrics']['memory_utilization_trend'].append(sample_results['avg_memory_utilization'])
            
            # Increment sample number
            sample_num += 1
            
            # Wait until next sample
            next_sample_time = self.start_time + (sample_num - 1) * self.sampling_interval
            sleep_time = max(0, next_sample_time - time.time())
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def cleanup(self):
        """Clean up after the endurance test."""
        logger.info(f"Cleaning up endurance test: {self.name}")
        
        # Generate trend charts
        self.generate_trend_charts()
    
    def generate_trend_charts(self):
        """Generate trend charts for the endurance test."""
        if not self.results['metrics']['samples']:
            return
        
        charts_dir = f"{self.report_dir}/charts"
        os.makedirs(charts_dir, exist_ok=True)
        
        # Extract data for charts
        sample_nums = [sample['sample_num'] for sample in self.results['metrics']['samples']]
        timestamps = [sample['timestamp'] - self.start_time for sample in self.results['metrics']['samples']]
        
        # Response time trend chart
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, self.results['metrics']['avg_response_time_trend'])
        plt.title(f"{self.name} - Response Time Trend")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Average Response Time (seconds)")
        plt.grid(True)
        plt.savefig(f"{charts_dir}/{self.name}_response_time_trend_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.close()
        
        # Throughput trend chart
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, self.results['metrics']['throughput_trend'])
        plt.title(f"{self.name} - Throughput Trend")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Throughput (requests/second)")
        plt.grid(True)
        plt.savefig(f"{charts_dir}/{self.name}_throughput_trend_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.close()
        
        # Error rate trend chart
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, self.results['metrics']['error_rate_trend'])
        plt.title(f"{self.name} - Error Rate Trend")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Error Rate (%)")
        plt.grid(True)
        plt.savefig(f"{charts_dir}/{self.name}_error_rate_trend_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.close()
        
        # Resource utilization trend chart
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, self.results['metrics']['cpu_utilization_trend'], label='CPU')
        plt.plot(timestamps, self.results['metrics']['memory_utilization_trend'], label='Memory')
        plt.title(f"{self.name} - Resource Utilization Trend")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Utilization (%)")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"{charts_dir}/{self.name}_resource_trend_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.close()

class APIResponseTimeTest(PerformanceTest):
    """Base class for API response time tests."""
    
    def __init__(self, name, description, endpoints, iterations=10):
        """
        Initialize the API response time test.
        
        Args:
            name (str): Name of the test.
            description (str): Description of the test.
            endpoints (dict): Dictionary of API endpoints to test.
            iterations (int): Number of iterations for each endpoint.
        """
        super().__init__(name, description, 'api_response')
        self.endpoints = endpoints
        self.iterations = iterations
    
    def setup(self):
        """Set up the API response time test."""
        logger.info(f"Setting up API response time test: {self.name}")
        logger.info(f"Endpoints: {self.endpoints}")
        logger.info(f"Iterations: {self.iterations}")
        
        # Initialize metrics
        self.results['metrics'] = {
            'endpoints': {}
        }
        
        for endpoint_name in self.endpoints:
            self.results['metrics']['endpoints'][endpoint_name] = {
                'response_times': [],
                'avg_response_time': 0,
                'min_response_time': 0,
                'max_response_time': 0,
                'p95_response_time': 0
            }
    
    def run(self):
        """Run the API response time test."""
        logger.info(f"Running API response time test: {self.name}")
        
        for endpoint_name, endpoint_url in self.endpoints.items():
            logger.info(f"Testing endpoint: {endpoint_name} ({endpoint_url})")
            
            response_times = []
            
            for i in range(self.iterations):
                try:
                    start_time = time.time()
                    response = requests.get(endpoint_url)
                    end_time = time.time()
                    
                    response_time = end_time - start_time
                    response_times.append(response_time)
                    
                    logger.info(f"Iteration {i+1}/{self.iterations}: Response time {response_time:.3f} seconds")
                    
                    # Add a small delay between requests
                    time.sleep(0.5)
                except Exception as e:
                    logger.error(f"Error testing endpoint {endpoint_name}, iteration {i+1}: {str(e)}")
            
            # Calculate metrics for this endpoint
            if response_times:
                self.results['metrics']['endpoints'][endpoint_name]['response_times'] = response_times
                self.results['metrics']['endpoints'][endpoint_name]['avg_response_time'] = statistics.mean(response_times)
                self.results['metrics']['endpoints'][endpoint_name]['min_response_time'] = min(response_times)
                self.results['metrics']['endpoints'][endpoint_name]['max_response_time'] = max(response_times)
                self.results['metrics']['endpoints'][endpoint_name]['p95_response_time'] = np.percentile(response_times, 95)
    
    def cleanup(self):
        """Clean up after the API response time test."""
        logger.info(f"Cleaning up API response time test: {self.name}")
        
        # Generate comparison chart
        self.generate_comparison_chart()
    
    def generate_comparison_chart(self):
        """Generate a comparison chart for the API endpoints."""
        if not self.results['metrics']['endpoints']:
            return
        
        charts_dir = f"{self.report_dir}/charts"
        os.makedirs(charts_dir, exist_ok=True)
        
        # Extract data for chart
        endpoint_names = list(self.results['metrics']['endpoints'].keys())
        avg_response_times = [self.results['metrics']['endpoints'][name]['avg_response_time'] for name in endpoint_names]
        p95_response_times = [self.results['metrics']['endpoints'][name]['p95_response_time'] for name in endpoint_names]
        
        # Create bar chart
        x = np.arange(len(endpoint_names))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(x - width/2, avg_response_times, width, label='Average')
        ax.bar(x + width/2, p95_response_times, width, label='95th Percentile')
        
        ax.set_title(f"{self.name} - API Response Times")
        ax.set_xlabel("Endpoint")
        ax.set_ylabel("Response Time (seconds)")
        ax.set_xticks(x)
        ax.set_xticklabels(endpoint_names, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, axis='y')
        
        fig.tight_layout()
        plt.savefig(f"{charts_dir}/{self.name}_comparison_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.close()
