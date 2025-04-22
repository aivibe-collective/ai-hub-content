# Learning Module: Understanding Popular LLMs for Your SME

## 1. Introduction: LLMs and Your Small Business

Welcome! This module explores Large Language Models (LLMs) – a powerful type of Artificial Intelligence (AI) – and how they can benefit Small and Medium Enterprises (SMEs) like yours, especially when working with budget constraints.

**What are LLMs?**
Think of LLMs as highly advanced AI assistants trained on vast amounts of text data. They can understand, generate, summarize, translate, and interact using human-like language. You've likely encountered them in tools like ChatGPT or Google Bard (now Gemini).

**Why Should SMEs Care?**
In today's competitive landscape, efficiency is key. LLMs can help SMEs:
*   **Automate Tasks:** Handle routine customer inquiries, draft emails, generate reports.
*   **Enhance Marketing:** Create engaging social media posts, product descriptions, and marketing copy.
*   **Improve Customer Service:** Power 24/7 chatbots to answer frequently asked questions.
*   **Boost Productivity:** Summarize long documents, brainstorm ideas, assist with writing.

**Open Source vs. Proprietary:**
LLMs come in two main flavours:
*   **Proprietary:** Owned by companies (like OpenAI, Google, Anthropic). Typically easier to use via paid services but offer less control.
*   **Open Source:** Code and model are publicly available (like Meta's Llama, Mistral AI models). Can be cheaper (or free, excluding hosting costs) and offer more control, but often require more technical setup.

**Module Goal (SMART Objective):**
By the end of this module, you will be able to **compare at least 3 LLM options (including their cost structures) and identify the most suitable one for a specific use case within your business**, keeping economic sustainability in mind.

## 2. What are Large Language Models (LLMs)?

At its core, an LLM is an AI program designed to process and generate text. Imagine an incredibly well-read assistant who has learned patterns, grammar, facts, and reasoning abilities from billions of webpages, books, and articles.

**Key Concepts (Simplified):**

*   **Training Data:** The massive amount of text the LLM learned from. The quality and diversity of this data influence the LLM's knowledge and potential biases.
*   **Parameters:** Think of these as the "neurons" or connections in the LLM's "brain." More parameters generally mean a more capable (but also potentially more expensive and resource-intensive) model. You'll hear terms like "7B model" (7 billion parameters) or "175B model."
*   **Prompt:** The instruction or question you give to the LLM. Crafting good prompts is key to getting useful results.
*   **Output/Generation:** The text the LLM produces based on your prompt.

LLMs don't "think" or "understand" like humans do. They are sophisticated pattern-matching machines, predicting the next most likely word in a sequence based on the prompt and their training data.

## 3. How Do LLMs Work (Simplified)?

Using an LLM generally follows a simple process from the user's perspective:

1.  **Input (Your Prompt):** You type a question or command into an interface (like a chat window or an application).
    *   *Example:* "Draft a short welcome email for new customers who signed up for our newsletter."
2.  **LLM Processing:** The LLM analyzes your prompt, breaks it down, and uses its internal knowledge (learned patterns) to figure out the best response.
3.  **Output (Generated Text):** The LLM generates the text based on its analysis and prediction.
    *   *Example:* The LLM writes a draft welcome email.

**How SMEs Access LLMs:**

*   **Proprietary Models:** Usually accessed via an **API (Application Programming Interface)**. This is like a digital "waiter" – your software sends a request (your prompt) to the LLM company's servers via the API, and the API brings back the response (the generated text). You typically pay based on how much you use (per "token," roughly a word or part of a word).
*   **Open Source Models:**
    *   **Self-Hosting:** You download the model and run it on your own computers or cloud servers. This requires technical knowledge and managing infrastructure.
    *   **Managed Hosting/APIs:** Some companies offer hosted versions of popular open-source models via APIs, similar to proprietary ones but often cheaper (e.g., Hugging Face Inference Endpoints, Groq, Perplexity).

## 4. Popular LLMs: Open Source vs. Proprietary

Let's look at some popular options relevant to SMEs:

### Proprietary LLMs

These are generally easier to start with but involve ongoing costs and less data control.

*   **OpenAI's GPT Models (e.g., GPT-3.5 Turbo, GPT-4, GPT-4o):**
    *   *Strengths:* Highly capable, versatile, widely integrated into other tools, easy-to-use API. GPT-4o offers strong performance with lower cost than GPT-4.
    *   *Weaknesses:* Can be expensive at scale (especially GPT-4), data privacy policies need careful review (though OpenAI offers options like zero data retention for API users).
    *   *Good for:* General purpose tasks, content creation, complex instructions when top quality is needed.
*   **Google's Gemini Models (e.g., Gemini Pro, Gemini Advanced/Ultra):**
    *   *Strengths:* Strong performance, integrates well with Google Cloud and Workspace, competitive pricing (Gemini Pro).
    *   *Weaknesses:* Newer API ecosystem compared to OpenAI, pricing tiers still evolving.
    *   *Good for:* Businesses using Google Cloud, multimodal tasks (processing text and images), general purpose AI needs.
*   **Anthropic's Claude Models (e.g., Claude 3 Haiku, Sonnet, Opus):**
    *   *Strengths:* Strong focus on AI safety and ethics ("Constitutional AI"), excellent for writing and conversation, large context window (can handle long documents). Haiku is very cost-effective.
    *   *Weaknesses:* API access might have waitlists initially, Opus (highest tier) is expensive.
    *   *Good for:* Customer service interactions, summarizing long reports, tasks requiring nuanced language.

**Pros for SMEs:**
*   Quick setup, no server management needed.
*   Access to state-of-the-art performance.
*   Pay-as-you-go pricing allows starting small.

**Cons for SMEs:**
*   Costs can escalate with usage.
*   Less control over the model and your data (depending on terms).
*   Risk of vendor lock-in.

### Open Source LLMs

These offer potential cost savings and more control but require technical resources or reliance on third-party hosting.

*   **Meta's Llama Series (e.g., Llama 2, Llama 3):**
    *   *Strengths:* Very strong performance (Llama 3 is competitive with mid-tier proprietary models), permissive license allows commercial use, large community support. Available in different sizes (e.g., 8B, 70B parameters).
    *   *Weaknesses:* Requires technical setup for self-hosting, performance depends heavily on the hardware used.
    *   *Good for:* SMEs with technical capacity or using managed hosting, cost-sensitive applications needing good performance.
*   **Mistral AI Models (e.g., Mistral 7B, Mixtral 8x7B):**
    *   *Strengths:* Highly efficient (good performance for their size), open Apache 2.0 license, strong multilingual capabilities. Mistral 7B runs well on lower-cost hardware. Mixtral uses a "Mixture of Experts" approach for efficiency.
    *   *Weaknesses:* Newer ecosystem than Llama, requires setup/hosting.
    *   *Good for:* Cost-sensitive applications, edge computing (potentially), SMEs needing efficient performance.
*   **Hugging Face Hub:**
    *   *Not an LLM itself,* but a crucial platform. It hosts thousands of open-source models (including Llama, Mistral, and many others), datasets, and tools. Offers "Inference Endpoints" for easy API access to many open-source models (paid service).
    *   *Good for:* Finding, comparing, and accessing open-source models without deep technical expertise (using their paid services) or for downloading models to self-host.

**Pros for SMEs:**
*   Potential for significantly lower costs (especially if self-hosted effectively).
*   Full control over data (if self-hosted).
*   No vendor lock-in; freedom to switch models.
*   Ability to fine-tune models on specific company data (advanced).

**Cons for SMEs:**
*   Requires technical expertise for setup and maintenance (self-hosting).
*   Infrastructure costs (servers, cloud computing).
*   Performance might lag behind the absolute top-tier proprietary models for some tasks.
*   Finding reliable managed hosting adds cost, though often less than proprietary APIs.

## 5. Applications for SMEs

How can you actually *use* these LLMs in your business?

*   **Customer Service:**
    *   *Example:* Power a website chatbot to answer common questions like "What are your business hours?" or "How do I track my order?" instantly, 24/7.
*   **Marketing & Sales:**
    *   *Example:* Generate ideas for blog posts targeting local customers. Draft social media updates announcing a new product. Write compelling product descriptions for your online store. Create personalized email marketing templates.
*   **Content Creation:**
    *   *Example:* Outline a business plan. Draft internal memos or announcements. Summarize lengthy industry reports to quickly grasp key insights. Generate frequently asked questions (FAQs) for your product/service.
*   **Internal Operations:**
    *   *Example:* Summarize transcripts of customer calls or meetings. Help draft job descriptions. Organize notes and extract action items.

Start with tasks that are repetitive, time-consuming, or where a helpful draft can save significant effort.

## 6. Limitations and Considerations

LLMs are powerful, but not perfect. Keep these points in mind:

*   **Accuracy & "Hallucinations":** LLMs can sometimes generate incorrect or nonsensical information (known as "hallucinations"). **Always fact-check critical information** generated by an LLM before using it.
*   **Bias:** LLMs learn from human-generated text, which contains biases. Their outputs may reflect societal biases (gender, race, etc.). Be mindful of this, especially in customer-facing or HR applications.
*   **Data Privacy & Security:** Be cautious about inputting highly sensitive customer or company data into public LLM tools.
    *   *Proprietary:* Check the provider's data usage and privacy policies carefully. Many offer business tiers with better privacy controls.
    *   *Open Source (Self-hosted):* You control the data, but you are responsible for securing your infrastructure.
*   **Cost Management:**
    *   *Proprietary:* API usage can add up quickly. Monitor your usage and set budgets.
    *   *Open Source:* Factor in hosting costs (cloud servers, electricity) and personnel time for setup/maintenance.
*   **Technical Skill Requirements:** Using APIs requires some basic technical understanding. Self-hosting open-source models requires significant technical expertise (or paying for a managed service).
*   **Context Window:** LLMs have a limit to how much text they can "remember" within a single conversation or prompt. For very long tasks, you might need to break them down.

## 7. Pillar Focus: SME Relevance

LLMs are highly relevant for SMEs precisely because they can help overcome common challenges:

*   **Resource Amplification:** LLMs act as a force multiplier. A small team can use LLMs to automate tasks that would otherwise require more staff (e.g., initial customer support, drafting content).
*   **Leveling the Playing Field:** Access to powerful AI is no longer limited to large corporations. SMEs can leverage LLMs (especially cost-effective proprietary tiers or open-source options) to implement sophisticated solutions for marketing, customer service, and operations.
*   **Efficiency Gains:** Automating routine text-based tasks frees up valuable time for SME owners and employees to focus on core business activities, strategy, and customer relationships.
*   **Enhanced Capabilities:** SMEs can offer services previously difficult to scale, like personalized marketing emails or instant responses to customer queries, improving customer satisfaction and competitiveness.

*Example:* A local bakery owner (SME) with limited marketing budget can use an LLM to generate creative social media post ideas, draft descriptions for new seasonal items, and even respond to simple customer inquiries on Facebook Messenger after hours.

## 8. Pillar Focus: Economic Sustainability

Choosing and using LLMs wisely is crucial for long-term economic sustainability:

*   **Cost-Effectiveness Analysis:** Don't just look at the sticker price. Consider the Total Cost of Ownership (TCO).
    *   *Proprietary:* Predictable per-use cost, but can scale high. Easy to start cheap.
    *   *Open Source (Self-hosted):* Minimal software cost, but requires investment in hardware/cloud resources and technical staff time (which has a cost!).
    *   *Open Source (Managed):* A middle ground, often cheaper than proprietary APIs but more expensive than self-hosting.
*   **Avoiding Vendor Lock-in:** Relying solely on one proprietary provider can be risky if prices increase or terms change. Exploring open-source options or ensuring your implementation can switch providers offers long-term flexibility.
*   **Scalability:** Pay-per-use proprietary models scale costs directly with usage, which can be good for managing cash flow initially. Open-source hosting costs might be more fixed but need planning for growth.
*   **Return on Investment (ROI):** Focus on LLM applications that provide clear value. Does it save X hours of staff time per week (calculate labor cost savings)? Does it improve marketing conversion rates (measure revenue increase)? Quantifying the benefits helps justify the cost and ensures sustainable use.
*   **Start Small, Scale Smart:** Begin with low-cost tiers or free trials. Test open-source models on affordable hosting. Prove the value on a small scale before committing significant resources. Use the cost calculator concepts below to estimate.

*Example:* An SME using an LLM for customer support might compare the monthly cost of a proprietary API (e.g., $50/month for their usage) versus the cost of a small cloud server + estimated maintenance time for an open-source model (e.g., $30/month server + 2 hours staff time). They must also factor in the setup cost/time for the open-source option.

## 9. Practical Component: Comparison Matrix

This matrix compares a few representative models. *Prices and capabilities change rapidly; always check the provider's latest information.*

| Feature                  | OpenAI GPT-4o                 | Anthropic Claude 3 Haiku   | Meta Llama 3 8B (Self-Hosted) | Mistral 7B (Self-Hosted)    |
| :----------------------- | :---------------------------- | :------------------------- | :---------------------------- | :-------------------------- |
| **Type**                 | Proprietary                   | Proprietary                | Open Source                   | Open Source                 |
| **Primary Access**       | API                           | API                        | Download & Host               | Download & Host             |
| **Ease of Use (Beginner)** | High (API)                    | High (API)                 | Low (Requires Tech Skills)    | Low (Requires Tech Skills)  |
| **Potential Cost**       | Moderate API Fees (Pay-per-use) | Low API Fees (Pay-per-use) | Hosting + Staff Time Costs    | Hosting + Staff Time Costs  |
| **Key Strengths**        | High capability, multimodal, speed, popular | Fast, very low cost, good for conversations | Strong performance for size, good license, community | Very efficient, runs on cheaper hardware, good license |
| **Key Weaknesses**       | Cost can scale, data policy review needed | Less performant than Opus/Sonnet/GPT-4 | Requires setup/maintenance, infrastructure costs | Lower performance than larger models, requires setup |
| **Good For SMEs Who...** | Need top performance/features via easy API | Are highly cost-sensitive, need conversational AI | Have tech resources, want data control, cost-conscious | Are very cost-sensitive, have tech resources, need efficiency |

*Note:* Open Source models can also be accessed via paid managed APIs (e.g., Groq, Together AI, Hugging Face), offering higher ease of use but adding API fees, often still cheaper than top proprietary models.

## 10. Practical Component: Cost Calculator (Conceptual Guide)

You can't use a single calculator for all LLMs, as pricing models differ. Here’s how to *estimate* costs:

**A. Proprietary LLMs (API-based):**

1.  **Identify Your Use Case:** E.g., Answer 500 customer emails/month.
2.  **Estimate Usage Volume:**
    *   Average length of input (prompt) per email? (e.g., 100 tokens)
    *   Average length of output (response) per email? (e.g., 300 tokens)
    *   Total tokens per email = 100 + 300 = 400 tokens.
    *   Total tokens per month = 500 emails * 400 tokens/email = 200,000 tokens.
3.  **Find the Provider's Pricing:** Go to the LLM provider's website (OpenAI, Anthropic, Google AI). Find the pricing page for the specific model (e.g., Claude 3 Haiku, GPT-4o). Prices are usually per *million* tokens (MTo).
    *   Example Price (Hypothetical): Claude 3 Haiku - $0.25/MTo input, $1.25/MTo output.
4.  **Calculate Estimated Cost:**
    *   Input Cost: (500 emails * 100 input tokens/email) / 1,000,000 * $0.25 = $0.0125
    *   Output Cost: (500 emails * 300 output tokens/email) / 1,000,000 * $1.25 = $0.1875
    *   **Total Estimated Monthly API Cost:** $0.0125 + $0.1875 = $0.20 *(Note: Real-world costs will vary based on actual usage and current pricing. This example shows the method)*. Check for any free tiers or monthly minimums.

**B. Open Source LLMs (Self-Hosted):**

1.  **Estimate Hosting Needs:** What kind of server do you need? Smaller models (like Mistral 7B, Llama 3 8B) might run on a mid-range cloud VM (Virtual Machine) or a dedicated server. This depends heavily on the model size and expected traffic.
    *   *Example Cloud VM Cost:* $20 - $100+ per month (depending on CPU, RAM, and crucially, GPU if needed for performance).
2.  **Estimate Bandwidth Costs:** If usage is high, data transfer costs might apply. (Often low for moderate use).
3.  **Estimate Setup & Maintenance Time:**
    *   Initial Setup: How many hours for a technically skilled person? (e.g., 5-15 hours). Calculate this cost (e.g., 10 hours * $50/hour = $500 one-time, or amortized).
    *   Ongoing Maintenance: Updates, monitoring, troubleshooting (e.g., 2-5 hours/month). Calculate this cost (e.g., 3 hours * $50/hour = $150/month).
4.  **Total Estimated Monthly Cost:** Hosting Cost + Maintenance Cost (+ Amortized Setup Cost).
    *   *Example:* $50 (Hosting) + $150 (Maintenance Time) = $200/month.

**C. Open Source LLMs (Managed API):**

*   Similar calculation to Proprietary APIs, but check the pricing of the managed service provider (e.g., Groq, Together AI, Fireworks AI, Hugging Face Endpoints). Prices are often lower than proprietary models for comparable performance tiers.

**Worksheet Idea:** Create a simple spreadsheet listing your potential use cases, estimated monthly volume (queries, documents, etc.), and then columns to calculate estimated costs for 2-3 different LLM options (Proprietary API, Self-Hosted Open Source, Managed Open Source API).

## 11. Practical Component: Decision Guide

Use these questions to guide your choice:

1.  **What is your primary goal?**
    *   *High-quality content, complex tasks?* -> Lean towards top Proprietary (GPT-4o, Claude 3 Sonnet/Opus).
    *   *Customer service chatbot, summarization, general assistance?* -> Mid-tier Proprietary (GPT-3.5, Gemini Pro, Claude 3 Haiku) or capable Open Source (Llama 3, Mixtral) are good candidates.
    *   *Simple automation, internal tools?* -> Efficient Open Source (Mistral 7B, Llama 3 8B) or cheapest Proprietary tiers might suffice.

2.  **What is your monthly budget for this?**
    *   *Minimal (<$20/month):* Look for free tiers of proprietary models, or self-host very efficient open-source models (if you have existing hardware/low-cost hosting and tech skills). Consider managed open-source APIs with generous free tiers (if available).
    *   *Moderate ($50 - $200/month):* Compare costs of mid-tier proprietary APIs vs. managed open-source APIs vs. self-hosting smaller open-source models on cloud VMs.
    *   *Flexible (>$200/month):* You have options across the board – focus on performance and ease of use that best fits your needs. Top proprietary models or larger self-hosted models become feasible.

3.  **What is your team's technical expertise?**
    *   *None/Very Low:* Stick to proprietary APIs or very user-friendly platforms built on LLMs. Avoid self-hosting.
    *   *Some Comfort with APIs/Cloud:* Proprietary APIs are straightforward. Managed open-source APIs are also viable.
    *   *Strong Technical Skills (Linux, Servers, Cloud):* Self-hosting open-source models is a possibility, offering maximum control and potential cost savings.

4.  **How critical is data privacy and control?**
    *   *Very High (Sensitive Data):* Self-hosting open-source is the best option for complete control. Carefully vet privacy policies of proprietary APIs (look for business agreements with zero data retention).
    *   *Moderate:* Standard proprietary API agreements (with review) or managed open-source options are likely acceptable.

5.  **Do you need the absolute best performance, or is "good enough" okay?**
    *   *Need State-of-the-Art:* Often points to the latest, largest proprietary models (GPT-4o, Claude 3 Opus).
    *   *"Good Enough" for the Task:* Opens up many more cost-effective options, including smaller proprietary models and most open-source models.

**Decision Flow Summary:**

*   **Low Budget / Low Tech:** Start with free/cheap proprietary APIs (Haiku, maybe GPT-3.5/Gemini Pro free tiers) or managed open-source APIs (check Groq, Hugging Face free tiers).
*   **Cost Conscious / Tech Savvy / Data Control:** Strongly consider self-hosting efficient open-source models (Mistral 7B, Llama 3 8B).
*   **Performance Focused / Budget Available / Ease of Use:** Lean towards high-end proprietary APIs (GPT-4o, Claude 3 Sonnet/Opus, Gemini Advanced).
*   **Balanced Needs:** Compare mid-tier proprietary APIs (Claude 3 Haiku/Sonnet, Gemini Pro) vs. managed APIs for larger open-source models (Llama 3 70B via API).

## 12. Conclusion

Large Language Models offer exciting opportunities for SMEs to innovate, automate, and compete more effectively. Whether you choose a user-friendly proprietary service or explore the flexibility of open-source options depends entirely on your specific business needs, budget, technical resources, and strategic goals.

**Key Takeaways:**

*   LLMs can automate tasks, enhance marketing, improve service, and boost productivity for SMEs.
*   Proprietary LLMs offer ease of use and top performance but come with ongoing costs and less data control.
*   Open Source LLMs provide potential cost savings and data control but require technical expertise or managed hosting.
*   Carefully consider costs (API fees vs. hosting/staff time), data privacy, technical requirements, and the specific use case before choosing.
*   Start small, measure the ROI, and scale your LLM usage sustainably.

**Next Steps:**

1.  **Identify:** Pinpoint 1-2 specific, high-impact tasks in your business where an LLM could help (e.g., drafting email responses, generating social media ideas).
2.  **Explore:** Use the Comparison Matrix and Cost Calculator concepts to research 2-3 relevant LLM options (e.g., one proprietary, one open-source via managed API, maybe self-hosted if feasible). Check current pricing!
3.  **Experiment:** Sign up for free trials or use low-cost tiers of proprietary models. Explore platforms offering easy access to open-source models.
4.  **Evaluate:** Test the chosen LLMs on your specific task. Does the quality meet your needs? Are the costs sustainable?
5.  **Consult (If Needed):** If considering self-hosting open-source models, talk to a trusted IT advisor or consultant.

By taking a thoughtful, informed approach, you can leverage the power of LLMs to support your SME's growth and economic sustainability.

---
**Content ID:** LRN-BEG-008

## Sources

[zhao2023survey] Zhao, W. X., Zhou, K., Li, J., Tang, T., Wang, X., Qu, Y., Chen, Z., Zhang, J., Zhang, S., & Wen, J.-R. (2023). *A survey of large language models*. arXiv preprint arXiv:2303.18223. https://arxiv.org/abs/2303.18223

[dwivedi2023chatgpt] Dwivedi, Y. K., Kshetri, N., Hughes, L., Slade, E. L., Jeyaraj, A., Kar, A. K., Baabdullah, A. M., Koohang, A., Raghavan, V., Ahuja, M., Al-Busaidi, H. A., Zhou, M., Rana, N. P., Wamba, S. F., Janssen, M., Raman, R., Shaw, R., Gutierrez, A., Williams, M. D., ... Edwards, J. S. (2023). "So what if ChatGPT wrote it?" Multidisciplinary perspectives on opportunities, challenges and implications of generative conversational AI for research, practice and policy. *International Journal of Information Management*, *71*, 102642. https://doi.org/10.1016/j.ijinfomgt.2023.102642

[eloundou2023gpts] Eloundou, T., Manning, S., Mishkin, P., & Rock, D. (2023). *GPTs are GPTs: An early look at the labor market impact potential of large language models*. arXiv preprint arXiv:2303.10130. https://arxiv.org/abs/2303.10130

[touvron2023llama2] Touvron, H., Martin, L., Stone, K., Albert, P., Almahairi, A., Babaei, Y., Bashlykov, N., Batra, S., Bhargava, P., Bhosale, S., Bikel, D., Blecher, L., Canton Ferrer, C., Chen, M., Cucurull, G., Esiobu, D., Fernandes, J., Fu, J., Fu, W., ... Lample, G. (2023). *Llama 2: Open foundation and fine-tuned chat models*. arXiv preprint arXiv:2307.09288. https://arxiv.org/abs/2307.09288

[bommasani2021foundation] Bommasani, R., Hudson, D. A., Adeli, E., Altman, R., Arora, S., von Arx, S., Bernstein, M. S., Bohg, J., Bosselut, A., Brunskill, E., Brynjolfsson, E., Buch, S., Buffa, V., Carlos, J., Choi, Y., Clark, J., Corbin, C. D., Koh, P. W., ... Liang, P. (2021). *On the opportunities and risks of foundation models*. arXiv preprint arXiv:2108.07258. https://arxiv.org/abs/2108.07258


## Source Collection Metadata

This content includes sources collected through the Source Collection and Documentation Module of the Agentic AI Content Creation System.

**Collection Date**: 2025-04-22

**Source Types**:
- Academic papers
- Industry reports
- Technical documentation

**Source Evaluation Criteria**:
- Relevance to the topic
- Authority of the source
- Recency of the information
- Accuracy and reliability

## Source Evaluation Results

Sources were evaluated using the CRAAP framework (Currency, Relevance, Authority, Accuracy, Purpose).

| Source ID | Currency | Authority | Quality Rating |
|-----------|----------|-----------|-----------------|
| zhao2023survey | 5/5 | 3/5 | Good |
| dwivedi2023chatgpt | 5/5 | 5/5 | Good |
| eloundou2023gpts | 5/5 | 3/5 | Good |
| touvron2023llama2 | 5/5 | 3/5 | Good |
| bommasani2021foundation | 4/5 | 3/5 | Good |
