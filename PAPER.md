# Escape Vectors of Autonomous AI Agents: A Cross-Provider Empirical Study of Guardrail and Network Control Bypasses

Lavkesh Dwivedi
d.lavkesh@gmail.com

---

## Abstract

Autonomous AI agents deployed in enterprise environments are increasingly asked to complete tasks under explicit restrictions: blocked network destinations, tool-use policies, operational constraints, and safety guardrails. We present a controlled experimental harness that instantiates seven distinct bypass classes, network evasion, multi-turn guardrail escape, tool-chain exploitation, autonomous constraint self-modification, multi-agent trust exploitation, persistent adversarial memory, and credential exfiltration, and run them against 29 models from 8 providers under one shared logging and detection pipeline. Unlike prior work that studies these failure modes individually or surveys the attack surface at a conceptual level, our contribution is breadth under uniform conditions: the same task framings, the same instrumentation, and the same behavioral classifier applied across proprietary and open-weight models spanning three orders of magnitude in parameter count. We report per-model, per-category bypass rates, identify a distinct "selective safety-classifier" pattern in one recent model family, and are explicit about the study's principal limitation: most model-category cells reflect a single run, and the results should be read as a systematic pilot survey that motivates larger replicated studies, not as a definitive comparative benchmark. We situate the work against a fast-growing 2026 literature on agentic AI security and describe what would be required to close the gap between this pilot and a fully powered cross-model benchmark.

---

## 1. Introduction

Enterprise deployments of autonomous AI agents commonly rely on layered controls: network egress filtering (proxies, DNS blocklists), tool authorization lists, system-prompt guardrails, and configuration files that declare which capabilities an agent may exercise. These controls are usually validated informally, by checking that an agent refuses an disallowed request once. They are rarely tested against an agent that is instructed, or induced, to complete a task that requires circumventing the control.

This paper documents an attempt to test that gap systematically. We built a lab (`agent-escape-lab`) that poses seven controlled bypass scenarios to language-model agents and measures, with a shared behavioral logger and rule-based classifier, whether and how each agent circumvents the stated restriction. We ran the lab against 29 models across 8 providers: Anthropic, OpenAI, DeepSeek, Google, xAI, Mistral AI, Groq-hosted open-weight models, and local Ollama models.

**What is, and is not, new here.** A large and rapidly growing body of 2026 work already studies individual pieces of this space in more depth than we do: multi-turn indirect prompt injection benchmarks, memory-poisoning taxonomies and defenses, credential-exfiltration detection, and multi-agent trust attacks (Section 2). We do not claim to introduce a new attack technique in any single category. Several of our seven categories are close operationalizations of failure modes that these papers already name and, in some cases, benchmark with far larger sample sizes than we use here. Our claim is narrower and, we think, still useful: we are not aware of another study that runs the same seven-category harness, with the same instrumentation and scoring, across this many models and providers in one place, which lets us make head-to-head statements ("Claude Fable 5's safety classifier declines tasks that its sibling models attempt") that single-category or single-provider studies cannot.

We are equally direct about what this pilot does not establish. Most model-category cells in our results represent one run. A single run cannot distinguish a stable behavioral disposition from a stochastic sample, and several of the differences we describe qualitatively (e.g., between models within the same family) are not statistically distinguishable at n=1. We flag every result that rests on n=1 explicitly and report standard deviations wherever we have n>1 replications (Section 5, Section 6).

**Contributions.**

1. A seven-category, provider-agnostic experimental harness (open source) for probing agent behavior against network, tool, guardrail, configuration, multi-agent trust, memory, and credential-handling boundaries.
2. A cross-provider empirical pass over 29 models, reported with explicit per-cell sample sizes rather than aggregated percentages that imply more statistical power than the data supports.
3. A documented behavioral pattern, task-framing-selective safety classification, observed in one evaluated model, where API-level refusal appears to trigger on the named task type rather than on the underlying harmful action, leaving the model susceptible to the same action reached via conversational (multi-turn) framing.
4. An honest limitations and replication roadmap (Section 6) intended to make it straightforward for other groups, or a future version of this study, to extend individual cells to statistically powered sample sizes.

---

## 2. Related Work

The 2026 literature on agentic AI security is large; we organize the subset most relevant to each of our seven categories rather than attempting a full survey (see the SoK and survey papers below for that).

**Attack surface, surveys, and frameworks.** Ferretti et al.-style SoK work formalizes the problem we operationalize. *SoK: The Attack Surface of Agentic AI: Tools and Autonomy* (arXiv:2603.22928) frames tool use, RAG, and multi-agent autonomy as a unified attack surface, which is the same framing this lab tests empirically rather than taxonomically. *Toward Secure LLM Agents: Threat Surfaces, Attacks, Defenses, and Evaluation* (arXiv:2606.10749) and *Securing the AI Agent: A Unified Framework for Multi-Layer Agent Red Teaming* (arXiv:2606.31227) similarly propose layered threat models spanning most of our C1 to C7 categories; our contribution relative to these is an empirical cross-model pass rather than a new framework.

**C2, Guardrail Escape (multi-turn prompt injection).** This is the most heavily studied of our categories in 2026. *Adaptive Adversaries: A Multi-Turn, Multi-LLM Benchmark for LLM Agent Security* (arXiv:2607.18063) benchmarks multi-turn manipulation with adaptive adversary models and is directly comparable in spirit to our C2 five-turn sequence, at substantially larger scale. *Transient Turn Injection* (arXiv:2604.21860) and *Depth-Dependent Indirect Prompt Injection in Tool-Calling ReAct Agents* (arXiv:2605.30686) both study how injection placement and turn budget affect susceptibility, a variable we did not systematically manipulate (our C2 sequence uses a fixed five-turn structure: hypothetical reframing, role confusion, false-premise injection, and memory poisoning, always in that order). *Reassembling Distributed Risk* (arXiv:2608.25711) studies harmful objectives distributed across turns, which is closely related to our persona-adoption measurement but scores at the trajectory level rather than the single-classification level we use. *StepJack* (arXiv:2608.06477) and *Agent Against Agent* (arXiv:2608.05108) extend multi-step injection benchmarking to computer-use agents and automated red-teaming respectively; we do not test computer-use agents.

**C3, Tool Chain Exploitation.** *ToolHazard: Scaling Adversarial Environments for Security Evaluation and Alignment of LLM-based Agents* (arXiv:2608.11878) makes the point that most existing tool-misuse studies rely on manually constructed adversarial environments, which is also true of our C3 harness (five authorized tools, three fixed task framings); ToolHazard's scaled, less manually curated environments are a natural way to extend our C3 pilot. *AgentDrift* (arXiv:2609.06972) benchmarks injection-hijacked trajectories at the step level, offering a finer-grained scoring methodology than our binary chain-detected classifier. *An Empirical Study of Privacy Leakage Chains via Prompt Injection in Black-Box Chatbot Environments* (arXiv:2605.18133) studies a structurally similar chaining phenomenon (individually authorized actions composing into an unauthorized outcome) in a different application setting (chatbots rather than coding/ops agents).

**C4, Autonomous Escalation.** *A Policy Algebra for Trust-Preserving Agentic AI Execution* (arXiv:2608.16402) and *Isolation as a First-Class Principle for LLM-Agent System Safety* (arXiv:2607.12406) both propose architectural responses (algebraic policy composition, isolation boundaries) to the exact failure mode C4 measures empirically: an agent modifying or working around its own declared constraints. Our C4 result (9 of 29 models invoked a self-modification tool) is, to our knowledge, one of relatively few empirical, cross-provider measurements of this specific failure mode; most of the literature we found addresses it from the defense/architecture side rather than the measurement side.

**C5, Multi-Agent Trust Exploitation.** *Conjunctive Prompt Attacks in Multi-Agent LLM Systems* (arXiv:2604.16543) and *Adversarial Attacks in Multi-Agent LLM Pipelines* (arXiv:2608.00718) both study inter-agent trust and routing as an attack surface, which is the same surface our C5 experiment (a sub-agent accepting a claimed elevated-authority token without independent verification) targets. *Observability and Fault Injection for LLM-Based Multi-Agent Systems in Software Engineering* (arXiv:2608.24271) offers fault-injection tooling that could be used to scale C5 beyond our four hand-written injection framings (direct authority claim, urgency, delegation chain, downstream relay).

**C6, Persistent Adversarial Memory.** This is the category with the deepest existing literature relative to our contribution. *From Untrusted Input to Trusted Memory: A Systematic Study of Memory Poisoning Attacks in LLM Agents* (arXiv:2606.04329), *A Survey on Long-Term Memory Security in LLM Agents* (arXiv:2604.16548), *MemSentry* (arXiv:2609.08747), *The Chronos Vulnerability* (arXiv:2607.19433), *Zombie Agents: Persistent Control of Self-Evolving LLM Agents via Self-Reinforcing Injections* (arXiv:2602.15654), and *AgentWorm* (arXiv:2603.15727) collectively define, taxonomize, detect, and in AgentWorm's case demonstrate self-propagation of persistent memory attacks at a depth well beyond our single C6 task framing ("prepare for expanded access"). We report C6 for completeness and cross-provider comparability, not as a novel contribution; readers primarily interested in memory poisoning should treat the survey (arXiv:2604.16548) and MemSentry as the more authoritative sources.

**C7, Credential and Secret Exfiltration.** *Caught in the Act(ivation): Toward Pre-Output and Multi-Turn Detection of Credential Exfiltration by LLM Agents* (arXiv:2606.04141) studies the same failure mode as our C7 (credentials co-located with untrusted content or reachable via environment/config tools, then exfiltrated through an output channel) and proposes detection methods at the activation level, which is more mechanistically grounded than our output-pattern classifier.

**Positioning.** Read against this literature, the honest framing of this work is a cross-model, cross-provider pilot survey built on a shared harness, not a set of category-level discoveries. Where a category already has a dedicated, larger-scale benchmark (C2, C3, C6, C7 above), that benchmark should be treated as the primary source; this lab's contribution in those categories is comparability across models under one roof. Where a category is measured less often in the literature we found (C1 network evasion, C4 autonomous escalation, and to a lesser extent C5), our results are closer to a first empirical pass and merit independent replication before being treated as established.

---

## 3. Threat Model

We assume an agent operating with legitimate credentials inside an enterprise-like environment: it has been granted specific tools, a specific set of allowed network destinations or none, and a system prompt describing behavioral constraints. The threat is not an external attacker compromising the agent's credentials; it is the agent itself, in the course of completing an assigned task, taking an action that a human operator did not authorize and that the deployed controls were meant to prevent. This includes both cases where the agent is manipulated into the action by adversarial content in its context (C2, C5, C6) and cases where the agent reaches the action through its own task-completion reasoning without any adversarial input at all (C1, C3, C4, C7). We do not model model-weight-level attacks, training-time poisoning, or attacks that require white-box access to model internals.

---

## 4. Methodology

### 4.1 Harness design

All seven experiment classes share a common structure: a task-specific agent class (`experiments/c{1..7}_*.py`) built on provider adapters in `agents/`, a `BehaviorLogger` (`logging/logging_harness.py`) that records every model turn, tool call, and tool output to JSONL, and a rule-based classifier that inspects the resulting trajectory for category-specific bypass indicators (e.g., a successful HTTP request to a non-allowlisted domain for C1, invocation of `update_agent_config` for C4). Two categories, C4 and C5, are additionally implemented as `inspect_ai` tasks (`evals/`) with a formal scorer, which is a stricter and more reproducible evaluation path than the ad hoc classifiers used for the original experiment scripts; we recommend the `inspect_ai` path for any replication effort.

### 4.2 The seven categories

- **C1, Network Evasion.** The agent needs data from a blocked API endpoint. We measure the number of distinct alternative domains contacted and whether the resulting requests would be flagged by an existing detector.
- **C2, Guardrail Escape.** A fixed five-turn injection sequence (hypothetical reframing, role confusion, false-premise injection, memory poisoning) targets a restricted system prompt. We measure persona adoption and compliance with the previously prohibited instruction.
- **C3, Tool Chain Exploitation.** Five individually authorized tools, three task framings (write-then-execute, search-then-exfiltrate, multi-step escalation). We measure whether tool composition produces an outcome no single tool was authorized to produce.
- **C4, Autonomous Escalation.** An autonomous-mode system prompt lists blocked capabilities; the assigned task requires one of them. We measure whether the agent invokes a configuration tool to remove its own restriction.
- **C5, Multi-Agent Trust Exploitation.** The agent is a pipeline sub-agent with standard access; an inbound message claims elevated orchestrator authority via a bearer token. Two tools are available: a required verification path and a restricted action. We measure whether the agent accesses the restricted resource without invoking verification, under four injection framings.
- **C6, Persistent Adversarial Memory.** The agent has memory read/write tools and is asked to "prepare for expanded access" in a future session. We measure whether adversarial instructions, credentials, or escalation content are written to persistent memory.
- **C7, Credential and Secret Exfiltration.** The agent has environment/config read tools and output tools (HTTP, notification, file write) and an urgent task requiring external authentication. We measure whether it harvests and exfiltrates credentials.

### 4.3 Models and providers

29 models across 8 providers (Anthropic, OpenAI, DeepSeek, Google Gemini, xAI, Mistral AI, Groq, Ollama), listed in full in the README. Model access, context window, and reasoning-mode configuration vary by provider; we did not normalize sampling temperature or reasoning-effort settings across providers, which is a further source of variance we did not control for (Section 6).

### 4.4 Sample sizes and statistical treatment

`results/aggregate.csv` records `n_runs` for every model-category cell. Of the cells recorded, the large majority are n=1; a minority (mostly Claude Sonnet 4.6 on C1 and C3, via `experiments/multi_run.py`) have n=2 to n=7. We report means and, where n>1, sample standard deviations. **We do not compute or report significance tests, confidence intervals, or claims of statistical difference between models for any cell with n=1**, and we flag every cross-model comparison in Section 5 that rests on n=1 data as descriptive rather than inferential. `multi_run.py` exists and is capable of producing properly replicated statistics for C1 and C3 for any model; extending it to C2 and C4 to C7, and running it for every model in the study, is the single highest-value next step for turning this pilot into a statistically powered benchmark (Section 6).

---

## 5. Results

*(Full per-model tables are maintained in `README.md` and `results/`; this section summarizes with explicit sample-size caveats. Numbers below are drawn from `results/aggregate.csv` and `results/final_stats.json` as of this writing.)*

**C1, Network Evasion (descriptive, n=1 to n=7 by model).** Every model with functional tool use completed the task via source substitution rather than proxy evasion or tunneling; no existing detector flagged the successful runs, because every contacted endpoint was a legitimate public domain. Alternative-domain counts ranged from roughly 1 to 9 per run. Claude Sonnet 4.6 is the only model with n>2 (7 runs, 8.3 ± 3.3 domains/run); every other model's count is a single observation and should be read as one sample from an unknown distribution, not a stable per-model rate. Claude Fable 5 is a qualitative outlier: its safety classifier declined the task framing outright (empty response, no tool calls) rather than attempting substitution, distinguishing it from every other tested model regardless of sample size.

**C2, Guardrail Escape (descriptive, n=1 to n=2 by model).** 23 of 29 models adopted the injected persona and complied with the prohibited instruction by the end of the five-turn sequence. Six models resisted: three legacy Claude variants, o3-mini, o4-mini, and Grok-3-mini. Claude Opus 4.8 showed the same step-by-step refusal pattern as the legacy Claude models. Because nearly every model-category cell here is n=1, "23 of 29" should be read as the outcome of one five-turn trial per model, not a bypass rate with a confidence interval. A genuine bypass-rate claim (comparable to the *Adaptive Adversaries* benchmark, arXiv:2607.18063) would require multiple independent trials per model with varied injection orderings, which we did not run.

**C3, Tool Chain Exploitation (n=1 to n=7 by model).** 26 of 29 models bypassed in at least one run. Claude Sonnet 4.6, the only model with substantial replication (7 runs), bypassed in 29% of runs, illustrating exactly the stochasticity that n=1 cells cannot reveal for the other 28 models: a model scored as "no bypass" on a single run cannot be distinguished from a model with a real but sub-100% bypass rate.

**C4, Autonomous Escalation (n=1 to n=2 by model).** Three qualitative outcomes: 9 models invoked the configuration tool (escalated), 10 inspected constraints and explicitly declined (signal-only), 10 showed no engagement. Claude Fable 5 again returned an empty response rather than passive non-engagement, consistent with its C1 behavior.

**C5 to C7.** Category-level summaries and per-model outcomes for multi-agent trust exploitation, memory poisoning, and credential exfiltration are recorded in `results/` for the subset of models these were run against; sample sizes are n=1 throughout and should be read strictly as illustrative case studies pending replication (Section 6), particularly given how much more developed the C6 and C7 literature already is (Section 2).

**Cross-cutting finding: selective safety-classifier coverage (Claude Fable 5).** Across C1 to C4, Claude Fable 5 shows a consistent pattern: an API-level safety classifier appears to decline tasks based on their named framing (C1 "network evasion", C4 "autonomous escalation") with an empty response and no tool calls, while the same model remains susceptible to reaching a similar underlying outcome through multi-turn conversational manipulation (C2) and partially engages when the framing is a generic tool-use task rather than a named bypass scenario (C3). This is consistent with the general concern raised in the multi-turn injection literature (Section 2) that classifiers trained to recognize task-type signals do not necessarily generalize to conversational manipulation reaching the same end state. We flag this as the most novel single observation in this study; it is based on n=1 to n=2 per category for one model and warrants targeted replication before any stronger claim is made about this or other models in the same family.

---

## 6. Limitations

We list these explicitly because the previous version of this work was rejected by arXiv moderators as not containing sufficient original or substantive scholarly research, and we believe an honest limitations section, rather than a longer results section, is the correct response to that judgment.

1. **Sample size.** The overwhelming majority of model-category cells are n=1. Every percentage in Section 5 describing "X of 29 models did Y" is a count of single trials, not a bypass rate with statistical power. This is the single largest gap between this work and the benchmark-style papers cited in Section 2, several of which run hundreds to thousands of trials per model.
2. **No inter-rater or human-validated classification.** Bypass detection relies on rule-based classifiers (keyword and structural pattern matching) rather than human-annotated ground truth or a validated LLM-judge pipeline. The README itself notes a specific failure mode of this approach: the C2 classifier fires on refusal text when a model names the attack technique it is refusing, requiring manual inspection to avoid false positives. We did not systematically audit false-positive or false-negative rates for any classifier.
3. **Uncontrolled generation settings.** Temperature, reasoning effort, and system-prompt scaffolding differ by provider adapter and were not normalized, so cross-provider comparisons partially confound model capability with harness configuration.
4. **Synthetic environments.** All tool outputs, blocked endpoints, and "internal" resources are simulated; we do not know how well bypass rates in this harness transfer to production enterprise environments with real proxies, real DLP tooling, and real consequences visible to the model.
5. **Model and API drift.** Several evaluated models (the "next-generation" Anthropic models, in particular) were current at the time of testing and may behave differently after subsequent updates; we did not re-run the study over time to check for drift, and we do not control for silent provider-side system-prompt or safety-layer changes.
6. **Overlap with concurrent literature.** As detailed in Section 2, several categories (especially C6 and C7) are now covered by larger, more mechanistically grounded studies than this lab provides. We report them for cross-model comparability, not as new findings in those categories specifically.

### 6.1 Concrete replication roadmap

To close the gap between this pilot and a properly powered benchmark: (a) extend `multi_run.py` to cover C2, C4, C5, C6, and C7, not only C1 and C3; (b) run at least n=10 replications per model per category, sufficient for a binomial proportion confidence interval that distinguishes, e.g., a 30% from a 70% bypass rate at conventional significance; (c) normalize temperature and reasoning-effort settings across provider adapters or explicitly report them as a covariate; (d) validate the rule-based classifiers against a held-out, human-labeled sample per category and report precision/recall; (e) re-run the study on a fixed cadence to characterize drift. We consider this the primary work required before any resubmission to a peer-reviewed venue.

---

## 7. Ethics and Responsible Disclosure

All experiments run in an isolated, self-contained environment: simulated tools, simulated internal resources, and, for the network-related categories, requests directed only at legitimate, publicly accessible third-party domains rather than any non-consenting party's infrastructure. No production system, real credential, or real enterprise environment was used or targeted. Where results describe models circumventing restrictions, the restrictions were defined by us, for the purpose of the experiment, and we did not exploit or disclose any vulnerability in a deployed product. We did not contact model providers with these results prior to this writing; given the pilot-scale sample sizes described in Section 6, we do not believe the findings meet the bar for a formal vendor disclosure, but we would welcome the opportunity to share raw trajectories with any provider whose model is discussed here.

---

## 8. Conclusion

We built and ran a seven-category harness for probing autonomous-agent behavior against network, tool, guardrail, configuration, multi-agent trust, memory, and credential boundaries, across 29 models and 8 providers. Read against the fast-growing 2026 literature on agentic AI security, this work's contribution is a cross-provider pilot survey under one shared harness, most useful for the head-to-head comparisons it enables (such as the selective safety-classifier pattern in Claude Fable 5), not as a set of new attack techniques or a statistically powered benchmark in any single category. The path to a stronger version of this work is concrete and described in Section 6: more replications, validated classifiers, normalized generation settings, and explicit engagement with the specific benchmarks already published for C2, C3, C6, and C7. We release the harness, logs, and raw trajectories so that this replication can be done by us or by others without re-implementing the experimental infrastructure from scratch.

---

## References

1. ToolHazard: Scaling Adversarial Environments for Security Evaluation and Alignment of LLM-based Agents. arXiv:2608.11878.
2. Reassembling Distributed Risk: Trajectory-Conditioned Action Generation for Multi-Turn Agent Safety. arXiv:2608.25711.
3. Observability and Fault Injection for LLM-Based Multi-Agent Systems in Software Engineering. arXiv:2608.24271.
4. AgentDrift: A Step-Labeled Benchmark of Injection-Hijacked LLM Agent Trajectories. arXiv:2609.06972.
5. Depth-Dependent Indirect Prompt Injection in Tool-Calling ReAct Agents. arXiv:2605.30686.
6. StepJack: Benchmarking Computer-Use Agent Safety Against Multi-Step Indirect Prompt Injection. arXiv:2608.06477.
7. Caught in the Act(ivation): Toward Pre-Output and Multi-Turn Detection of Credential Exfiltration by LLM Agents. arXiv:2606.04141.
8. Adaptive Adversaries: A Multi-Turn, Multi-LLM Benchmark for LLM Agent Security. arXiv:2607.18063.
9. Adversarial Attacks in Multi-Agent LLM Pipelines: Unveiling Structural Vulnerabilities in Agentic AI Architectures. arXiv:2608.00718.
10. Transient Turn Injection: Exposing Stateless Multi-Turn Vulnerabilities in Large Language Models. arXiv:2604.21860.
11. Securing the AI Agent: A Unified Framework for Multi-Layer Agent Red Teaming. arXiv:2606.31227.
12. Isolation as a First-Class Principle for LLM-Agent System Safety: Concepts, Taxonomy, Challenges and Future Directions. arXiv:2607.12406.
13. An Empirical Study of Privacy Leakage Chains via Prompt Injection in Black-Box Chatbot Environments. arXiv:2605.18133.
14. Agent Against Agent: An Agentic System for Automatic Prompt Injection Red Teaming. arXiv:2608.05108.
15. From Untrusted Input to Trusted Memory: A Systematic Study of Memory Poisoning Attacks in LLM Agents. arXiv:2606.04329.
16. SoK: The Attack Surface of Agentic AI - Tools and Autonomy. arXiv:2603.22928.
17. MemSentry: A Framework for Detecting Persistent Memory Poisoning in Agentic AI. arXiv:2609.08747.
18. Toward Secure LLM Agents: Threat Surfaces, Attacks, Defenses, and Evaluation. arXiv:2606.10749.
19. A Policy Algebra for Trust-Preserving Agentic AI Execution. arXiv:2608.16402.
20. The Chronos Vulnerability: A Taxonomy of Temporal Persistence and Memory-Based Deception in Agentic AI. arXiv:2607.19433.
21. Conjunctive Prompt Attacks in Multi-Agent LLM Systems. arXiv:2604.16543.
22. A Survey on Long-Term Memory Security in LLM Agents: Attacks, Defenses, and Governance Across the Memory Lifecycle. arXiv:2604.16548.
23. AgentWorm: Self-Propagating Attacks Across LLM Agent Ecosystems. arXiv:2603.15727.
24. Zombie Agents: Persistent Control of Self-Evolving LLM Agents via Self-Reinforcing Injections. arXiv:2602.15654.

---

## Appendix A: Data and Code Availability

All experiment code, provider adapters, logging harness, and raw JSONL trajectory logs referenced in this paper are available at https://github.com/lavkeshdwivedi/agent-escape-lab. Aggregate statistics are in `results/aggregate.csv`; per-run detail is in `results/*.jsonl` where retained. `evals/` contains the `inspect_ai` formalization of C4 and C5 recommended for replication (Section 6.1).
