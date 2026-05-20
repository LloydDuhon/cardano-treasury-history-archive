# Treasury Fund 2 Prior Work Overlap Review

Generated: 2026-05-20T18:13:27Z
Mode: AI adjudicated
AI model: qwen3.5:4b
Retrieval shortlist depth: top 25 historical candidates per current proposal

Purpose: screen the 69 current TF2 proposals for historically similar Catalyst, Treasury Fund 1, on-chain treasury, and BuilderDAO work. This is a triage report, not a final audit finding.

Method: deterministic retrieval creates a top-candidate shortlist for each current proposal. Candidate-pair adjudication is then applied from the review JSONL. Manual console adjudications are human analyst judgments. Local AI screening rows are draft triage judgments produced by a workstation running Ollama with Qwen 3.5 4B; they require human review before being treated as final findings.

Counting caveat: BuilderDAO downstream rows are non-additive detail and should not be added to the TF1/on-chain parent amount.

## Adjudication Sources

- manual-console-adjudication: 25 candidate pairs
- qwen3.5:4b: 1700 candidate pairs

## Summary

- Current proposals reviewed: 69
- Candidate pairs in CSV: 1725
- Triage rows shown below: 123

## Proposal Reviews

### 2027 Objectives, Research validation & Market Pilots - IntersectCPC

- Current proposer: IntersectCPC
- Current requested budget: 1,240,000.00 ADA
- Triage matches: none.

### A High-Performance Partner Chain Factory using Ouroboros Tachýs

- Current proposer: Ensurable Systems Ltd
- Current requested budget: 13,150,479.00 ADA
- Triage matches: none.

### Amplify Cardano: Ecosystem Accelerator + Community-Led Marketing & Events Fund

- Current proposer: Rare Network (Rare Evo) & SCRIB3
- Current requested budget: 8,583,334.00 ADA
- Triage matches: 1

#### Project Catalyst: Amplify Cardano: Community-Led Marketing by Rare Network

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 0.00 ADA)
- Proposer relationship: different
- Retrieval: rank 1, score 0.281, shared terms: amplify, driving, funding, global, growth, lacks, led, marketing, network, projects
- Overlap evidence: Shared thematic focus on Cardano marketing and ecosystem acceleration; similar terminology ('Amplify Cardano', 'Community Led Marketing'); however, distinct strategic scopes (Tier 1 listings vs general visibility) and different execution models.
- Funding evidence: Historical proposal had 0.00 ADA funded despite approval status; current proposal budget is substantial (8.5M ADA); historical funding did not cover current scope.
- Relationship evidence: Different proposer entities (Rare Evo & SCRIB3 vs p-lido-0198bc20-0ab7-73ee-a1f8-6f38c9ef0f2f); low proposer similarity score (0.107).
- Review notes: While the titles and high-level goals overlap significantly, the specific work proposed differs in execution strategy and target outcomes. The previous proposal was approved but never funded, suggesting it may have been a conceptual or planning phase that did not result in actual resource allocation. The current proposal represents a new, larger-scale initiative with different proposers.
- Source: https://www.catalystexplorer.com/en/proposals/amplify-cardano-community-led-marketing-by-rare-network-f14

### Autonomous AI Finance on Cardano with ClawBank

- Current proposer: Justice Conder
- Current requested budget: 1,874,600.00 ADA
- Triage matches: 1

#### Project Catalyst: From Chat to Checkout: Autonomous AI Payments via Cardano

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 100,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 6, score 0.199, shared terms: agents, autonomous, case, chain, layer, mcp, real, secure, time, use
- Overlap evidence: Both proposals address autonomous AI agents performing financial transactions on Cardano, utilizing MCP and wallet provisioning. The current proposal expands this concept to include USDCx integration and multi-agent flows, while the historical proposal focused on one-time session tokens for small payments. Core concepts of 'autonomous', 'AI agents', 'Cardano rails', and 'MCP' are shared.
- Funding evidence: The historical proposal was not funded (status: unfunded/not_approved) and received no funding, so there is no prior funding overlap to assess.
- Relationship evidence: Different proposers identified (Justice Conder vs p-lido-b9e9a5b7-eb09-45fd-bf3b-17cf140fa504) with low proposer similarity score of 0.070.
- Review notes: The current proposal represents a substantial evolution of the autonomous AI payment concept on Cardano rather than a direct reuse of previous work. While the foundational idea of AI agents managing funds exists in both proposals, the specific implementations differ (session tokens vs. continuous wallet management/USDCx). The lack of prior funding means this is not a case of re-funding existing work, but rather building upon an unfunded concept with new technical scope.
- Source: https://www.catalystexplorer.com/en/proposals/from-chat-to-checkout-autonomous-ai-payments-via-cardano-f14

### BloxBean Java/JVM Toolchain for Cardano: 2026 Maintenance & New Initiatives

- Current proposer: BLOXBEAN
- Current requested budget: 432,600.00 ADA
- Triage matches: 2

#### On-chain TreasuryWithdrawals: Withdraw ₳99,600 for BloxBean Java Tools Maintenance and Enhancement

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 99,600.00 ADA)
- Proposer relationship: same
- Retrieval: rank 1, score 0.315, shared terms: based, bloxbean, budget, build, building, ccl, client, compatibility, contributors, custom
- Overlap evidence: Current proposal lists CCL, Yaci, Yaci Store, and Yaci DevKit as core projects requiring maintenance and new initiatives. Historical proposal explicitly requests funding for 'BloxBean Java Tools Maintenance and Enhancement' covering the exact same four tools (CCL, Yaci, Yaci Store, Yaci DevKit) with identical goals of ongoing maintenance, feature enhancements, and compatibility updates.
- Funding evidence: Current proposal seeks 432,600 ADA for 1.5 FTEs over 12 months including new initiatives (Yano, JuLC). Historical proposal sought 99,600 ADA for 1 additional FTE over 12 months for the same core tools. The current proposal represents a significant expansion of the previously funded scope from maintenance-only to include maturation of new projects.
- Relationship evidence: Same entity (BloxBean) requesting funding for identical toolchain projects (CCL, Yaci, Yaci Store, Yaci DevKit); Historical text explicitly states 'This proposal aims to solve the following problem: BloxBean has developed a suite of open source Java tools essential for Cardano developers...'
- Review notes: The current proposal is a direct continuation and expansion of the previously funded work by the same proposer (BloxBean). The core toolchain (CCL, Yaci, Yaci Store, Yaci DevKit) remains identical. While the historical funding was strictly for maintenance and one additional FTE, the current proposal maintains that scope while adding 0.5 FTE and new initiatives (Yano, JuLC), indicating a clear evolution of the same project rather than distinct work.
- Source: ipfs://bafkreibelpp2qzjcpeizeobf57tmhl4q6kauutytdve3mqzzjxzp2jqjxm

#### Treasury Fund 1: BloxBean Java Tools Maintenance and Enhancement

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 99,600.00 ADA)
- Proposer relationship: same
- Retrieval: rank 2, score 0.310, shared terms: bloxbean, building, ccl, client, custom, developer, devkit, documentation, files, full
- Overlap evidence: Current proposal explicitly lists CCL, Yaci, Yaci Store, and Yaci DevKit as core deliverables, which match the historical proposal's focus on these exact tools. The current proposal expands on maintenance by adding new initiatives (Yano, JuLC) but retains the foundational work of maintaining the existing toolchain described in the historical record.
- Funding evidence: Historical funding was for 1 FTE over 12 months; current proposal seeks 1.5 FTEs for 12 months, indicating an increase in scope and resources for the same core project.
- Relationship evidence: Same organization (BloxBean) and identical project scope (Java/JVM toolchain for Cardano)
- Review notes: The current proposal represents a continuation of the previously funded work with increased budget and expanded deliverables (new initiatives). The overlap is high because the core mission—maintaining and enhancing the BloxBean Java toolchain—is identical to the historical proposal. No new unrelated work is introduced; rather, it builds upon the existing foundation.
- Source: https://treasury.sundae.fi/budgets/9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619/project/EC-0019-25

### Bringing Real-World Payments to Cardano with Wirex

- Current proposer: Wirex Limited
- Current requested budget: 3,961,538.00 ADA
- Triage matches: none.

### Cardano 2030: A Techstars Strategy for Global Ecosystem Adoption & Utility.

- Current proposer: Techstars
- Current requested budget: 9,373,803.00 ADA
- Triage matches: 2

#### Project Catalyst: Techstars investment-readiness program for Cardano Builders

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 1,600,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 1, score 0.222, shared terms: active, builders, companies, network, pre, program, real, support, techstars, ventures
- Overlap evidence: Both proposals focus on accelerating Cardano builders into investment-ready companies through pre-accelerator programs and access to venture capital networks. The historical proposal explicitly mentions converting builders to companies via an investment readiness program, while the current proposal outlines a similar strategy of sourcing and scaling startups for adoption milestones.
- Funding evidence: Historical proposal was unfunded and over budget; current proposal seeks significant funding ($9.3M vs $1.6M historical request).
- Relationship evidence: Historical proposer is a Lido wallet address; current proposer is Techstars organization.
- Review notes: While the strategic goal of building accelerator programs for Cardano developers is consistent, the specific entities involved differ significantly (Lido wallet vs Techstars brand), and the historical proposal was not funded. The overlap lies in the methodology of pre-acceleration rather than identical work execution.
- Source: https://www.catalystexplorer.com/en/proposals/techstars-investment-readiness-program-for-cardano-builders-f12

#### Project Catalyst: Techstars will help Cardano Builders grow their businesses to drive Cardano's Adoption

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 1,079,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 3, score 0.212, shared terms: adoption, builders, building, drive, global, growth, its, network, support, techstars
- Overlap evidence: Both proposals focus on accelerating Cardano builders and startups to drive adoption. The historical proposal provided mentorship and masterclasses for early-stage builders, while the current proposal expands this into a formal accelerator program with specific verticals (DeFi, RWA) and community labs in NY/London. The core mission of 'growing builders' is consistent, but the scope has evolved from general support to a structured ecosystem strategy.
- Funding evidence: Historical funding was 1,079,000 ADA for builder growth. Current budget is 9,373,803 ADA for a broader ecosystem strategy including talent acquisition and community hubs. The current proposal represents a significant scale-up of the previously funded concept rather than a direct reuse of the same work.
- Relationship evidence: Current proposer is 'Techstars' (an organization), while historical proposer was 'p-lido-acd5045c-7cde-4496-bcd9-149550e4b3f1' (a wallet address). While the current proposal leverages Techstars' brand, the specific entity funding previously is distinct from the organization proposing now.
- Review notes: The proposals share a clear thematic lineage regarding builder acceleration, but they differ in proposer identity (wallet vs organization) and scope magnitude. The historical funding covered early-stage support; the current proposal covers a full accelerator lifecycle plus community infrastructure. This constitutes significant component reuse rather than identical work.
- Source: https://www.catalystexplorer.com/en/proposals/techstars-will-help-cardano-builders-grow-their-businesses-to-drive-cardanos-adoption-f13

### Cardano Activation Program (CAP)

- Current proposer: NMA Venture Capital GmbH
- Current requested budget: 6,200,600.00 ADA
- Triage matches: 1

#### On-chain TreasuryWithdrawals: Cardano x Draper Dragon: Orion Fund

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: full (yes; 50,000,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 2, score 0.222, shared terms: 27m, across, active, all, applications, based, blockchain, builders, cap, catalyst
- Overlap evidence: The current proposal explicitly states it creates the European pipeline for the previously funded Draper Orion Fund, with startups running Cardano flows by Q4 2026 becoming Orion Tranche 2 investment candidates. The historical text confirms a multi-year strategy where future tranches are requested via separate governance actions, and the current proposal mirrors this structure (Tranche 1 now, future tranches later). Both proposals target ecosystem growth, on-chain transactions, and TVL.
- Funding evidence: Historical funding was $50M ADA for a multi-year fund with future Treasury withdrawals planned. Current funding is $6.2M ADA for a milestone-gated program that feeds into the same Orion Fund pipeline. The current proposal's 'North Star' metric and use of Intersect smart contracts align with the historical fund's goal of generating measurable returns to the Treasury.
- Relationship evidence: NMA Venture Capital GmbH is a distinct entity from Draper Dragon Orion GP, LLC; proposer_similarity score is 0.000.
- Review notes: The current proposal represents a continuation of the previously funded Draper Orion Fund strategy, specifically targeting European startups as a precursor to the Orion Tranche 2 investments. While the proposers are different (NMA vs Draper Dragon), the work is highly overlapping as the current proposal is explicitly designed to operationalize the pipeline established in the historical proposal. The funding structure and ecosystem goals are consistent.
- Source: ipfs://QmPXYnQ65EuKCVPrWfDqFZmiF8Y4PzxZ87XrGs6UaMkNru

### Cardano app on Ledger maintained by Ledger Technologies SAS

- Current proposer: Ledger Technologies SAS
- Current requested budget: 2,060,000.00 ADA
- Triage matches: 2

#### Treasury Fund 1: VacuumLabs - Hardware Wallets Maintenance & Ledger App Rewrite

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 724,800.00 ADA)
- Proposer relationship: different
- Retrieval: rank 7, score 0.200, shared terms: app, features, hardware, integration, ledger, maintenance
- Overlap evidence: current proposal is for yearly maintenance of the Cardano app on Ledger hardware, while historical proposal was a funded contract for the same task (designing new UI, implementing changes, firmware updates, and ongoing maintenance) specifically for the Cardano Ledger App.
- Funding evidence: historical funding of 724,800.00 ADA covered the design, implementation, audit, and release phases of the app rewrite plus ongoing maintenance cycles; current proposal is a recurring fee for the exact same scope of work (maintenance and updates).
- Relationship evidence: different legal entities (Ledger Technologies SAS vs addr1q9c0wgxuygu6plh23kmxkl0wewypmgrewe706g8q0y5psdz32x5hqy5y2v0mt7hgsd2mpm3cwqwhzevrh6sn04gfg5nsj6r0a)
- Review notes: The current proposal represents a continuation of the work initiated in the historical proposal. The core deliverables (maintaining the Cardano app on Ledger hardware, updating firmware/integration libraries, and ensuring security/performance) are identical. Although the proposer is a different entity (likely a successor or related party), the work itself is not new but rather an extension of previously funded activities.
- Source: https://treasury.sundae.fi/budgets/9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619/project/EC-0011-25 EC-0005-25

#### Project Catalyst: Ledger Live Integration Maintenance

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: significant_partial
- Previously proposed: True
- Previously funded relevance: none (yes; 200,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 3, score 0.212, shared terms: integration, ledger, maintenance
- Overlap evidence: Both proposals address the maintenance of the Cardano Ledger Live integration, but the historical proposal was funded by a third party while the current proposal is for direct funding to Ledger Technologies SAS
- Funding evidence: Historical funding was 200,000.00 ADA; current budget is 2,060,000.00 ADA, indicating a significant increase in scope or duration
- Relationship evidence: Historical proposer is a distinct entity (p-lido-255c7184-767e-4799-ba86-c08935214161) compared to current proposer (Ledger Technologies SAS)
- Review notes: The work overlap is moderate as both proposals target the same integration but differ in proposer and funding structure. The historical proposal was completed, suggesting the maintenance need persists. The current proposal's higher budget warrants scrutiny for potential scope creep beyond simple maintenance.
- Source: https://www.catalystexplorer.com/en/proposals/ledger-live-integration-maintenance-f10

### Cardano Budget Committee: Budget Process Improvement and Treasury Transparency (2026–2027)

- Current proposer: IntersectCBC
- Current requested budget: 600,000.00 ADA
- Triage matches: none.

### Cardano Builder DAO

- Current proposer: Cardano Builder DAO
- Current requested budget: 20,600,000.00 ADA
- Triage matches: 2

#### On-chain TreasuryWithdrawals: Withdraw ₳12,000,000 for Cardano Builder DAO administered by Intersect

- Match confidence: high
- Estimated current-work overlap: 95%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 12,000,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 1, score 0.382, shared terms: accountability, across, active, aligned, application, been, budget, builder, builders, built
- Overlap evidence: The current proposal is the expansion of the framework piloted in 2025 (historical period). The historical text details the funding of the 'Cardano Builder DAO' which provides 'sustainable financial backing' for 'high impact projects'. The current proposal states: 'The CB DAO was the first successful pilot of the Initiative DAO framework in 2025.' This confirms the work is the same entity, just a subsequent budget cycle expansion.
- Funding evidence: Historical amount: 12,000,000.00 ADA. Current amount: 20,600,000.00 ADA. The historical action was a 'withdrawal_action' for the Cardano Builder DAO administered by Intersect.
- Relationship evidence: The current proposal describes the CB DAO as a 'smart contract enforced, member governed funding mechanism'. The historical text confirms this exact same entity ('Cardano Builder DAO') was funded via a treasury withdrawal administered by Intersect. The purpose, metrics (TVL, active users), and governance structure described are identical.
- Review notes: This is a direct continuation of previously funded work. The current proposal represents the next budget cycle (2026) for the same entity (Cardano Builder DAO) that received funding in the previous cycle via Intersect's administration. The overlap is not merely textual but represents the same organizational entity and mission. The proposer change from Intersect to 'Cardano Builder DAO' reflects a shift from vendor administration to direct governance, as described in the text.
- Source: ipfs://bafkreidlb2fusg7asmfcnugcrzmfkhk6sb32b4st5ieji2q3oxmbhm6sma

#### Treasury Fund 1: Rainfire DAO - Cardano Builder DAO 

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 12,000,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 2, score 0.344, shared terms: active, application, builder, contract, dao, funding, governed, growth, mechanism, members
- Overlap evidence: The current proposal is explicitly described as an expansion of the Initiative DAO Framework, which was piloted in 2025 by the exact same proposer. The historical text outlines milestones for launching the CB DAO (Milestones 1-4), while the current proposal describes the operational framework and governance structure established during that pilot. The current proposal's goal to 'expand a proven model' directly references the work already funded in the historical record.
- Funding evidence: The historical proposal received 12,000,000.00 ADA under the status 'contracted', indicating execution of the core framework. The current proposal seeks 20,600,000.00 ADA to expand this framework to other ecosystem parts, confirming continuity of the project rather than a new independent initiative.
- Relationship evidence: Identical proposer address (addr1qxnuhkxz0mgh0vx6jg9zg4qp9pg27ckm6uv622fsxtghap3sruuxr0ev6mn5907qz4wl4s6qvsygmvrdc5qzwq0mlrwsannve8) and identical project title 'Cardano Builder DAO' indicate the same entity.
- Review notes: The proposal represents a direct continuation and expansion of previously funded work by the same entity. The historical record confirms the successful pilot of the 'Cardano Builder DAO' framework in 2025. The current proposal does not introduce new foundational work but rather seeks to scale an existing, funded model. Per the definition of high confidence (overlap >= 60%), this constitutes substantial reuse where the historical work covers the core mechanism and governance structure proposed now.
- Source: https://treasury.sundae.fi/budgets/9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619/project/EMI-0004-25

### Cardano Business Development Network: Accelerating Enterprise Adoption Through Coordinated BD Hubs 

- Current proposer: Yoram Ben Zvi
- Current requested budget: 1,519,250.00 ADA
- Triage matches: 1

#### Project Catalyst: Getting down to business! Building the Professional Decentralised Business Development Network

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 402,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 11, score 0.192, shared terms: building, business, companies, development, growth, infrastructure, leads, network, partners, partnerships
- Overlap evidence: Both proposals address the creation of a decentralized business development network to connect Cardano companies with partners and generate leads. The core objective of building infrastructure for enterprise adoption is consistent, though the current proposal specifies a regional hub model with specific team structures (5 teams), while the historical proposal focused on a general 'decentralised partnership creation solution'.
- Funding evidence: The historical proposal was not approved and received no funding. The current proposal represents a new initiative with a significantly larger budget.
- Relationship evidence: None identified; proposers are distinct entities (Yoram Ben Zvi vs. Lido Foundation addresses).
- Review notes: While the strategic direction (building a BD network) is highly similar, the specific implementation details differ. The historical proposal was unfunded and proposed by Lido Foundation addresses, whereas the current proposal is led by Yoram Ben Zvi. The overlap is significant in concept but not substantial enough to be considered high confidence reuse given the lack of prior funding and different proposer identity.
- Source: https://www.catalystexplorer.com/en/proposals/getting-down-to-business-building-the-professional-decentralised-business-development-network-f10

### Cardano Content Creator Consortium (C4): Ecosystem Video Content Production, Marketing & Education

- Current proposer: Cardano Content Creator Consortium (C4)
- Current requested budget: 1,524,400.00 ADA
- Triage matches: none.

### Cardano DeFi & OpenFi US App-Layer Demand Activation Program

- Current proposer: Magenta Labs
- Current requested budget: 2,500,000.00 ADA
- Triage matches: none.

### Cardano DeFi Deployment Execution Program

- Current proposer: Magenta Labs
- Current requested budget: 2,950,000.00 ADA
- Triage matches: none.

### Cardano Enterprise Activation Sandbox

- Current proposer: STORM Partners
- Current requested budget: 929,699.00 ADA
- Triage matches: none.

### Cardano Enterprise Adoption: Production Ticketing Platform

- Current proposer: Anvil Development Agency, Inc.
- Current requested budget: 4,372,865.00 ADA
- Triage matches: 2

#### Project Catalyst: Sellout x Anvil: Fraud-Proof Ticketing and Events on Cardano

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (no; 700,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 1, score 0.241, shared terms: anvil, enterprise, event, marketplace, revenue, sellout, system, that, through, ticket
- Overlap evidence: Current proposal is Phase 2 of the exact same system (Sellout x Anvil ticketing) as the historical proposal; historical work covered fraud-proof ownership, resale marketplace, and royalty enforcement which are now expanded to include anti-scalping controls, wallet onboarding, and security audits.
- Funding evidence: Historical funding was $700k ADA for Phase 1 (live deployment); current request is $4.37M ADA for Phase 2 (scaling), representing a continuation of the same project lifecycle rather than new independent work.
- Relationship evidence: Anvil Development Agency is explicitly named as the builder in both proposals; historical proposer address p-lido-0f41c58b-1062-4ea9-9ca3-76fd37fe5009 aligns with Anvil's operational identity.
- Review notes: The proposal represents a direct continuation of previously funded work by the same entity. The historical project successfully deployed core ticketing features on Cardano mainnet; this current request funds the expansion and enterprise scaling of that exact system. No new foundational work is being proposed, only incremental development within an established framework.
- Source: https://www.catalystexplorer.com/en/proposals/sellout-x-anvil-fraud-proof-ticketing-and-events-on-cardano-f15

#### BuilderDAO downstream disbursement: BuilderDAO Round 2: Anvil Development Agency

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (non_additive; 85,000.00 ADA downstream; non-additive with EMI-0004-25)
- Proposer relationship: same
- Retrieval: rank 17, score 0.184, shared terms: 200, agency, anvil, development, production, revenue
- Overlap evidence: Current proposal is explicitly defined as Phase 2 of the same production ticketing system described in historical funding; Phase 1 was already live with no Cardano treasury funding, indicating this current request covers the remaining critical infrastructure for mass adoption rather than new work.
- Funding evidence: Historical record shows non-additive downstream disbursement (85k ADA) specifically for Anvil's onchain transaction goals and API key issuance, which are foundational components of the current Phase 2 proposal.
- Relationship evidence: Exact proposer match (Anvil Development Agency) and identical project scope evolution from Phase 1 to Phase 2.
- Review notes: The proposal represents a continuation of previously funded work by the same entity. The historical funding covered initial onchain transaction volume and API infrastructure (Phase 1), while the current request targets scaling that existing system with enterprise features like marketplaces, royalties, and security audits. Given the explicit Phase 2 designation and identical proposer, this is not new work but an expansion of a previously funded project.
- Source: https://cbdao.taptools.io/

### Cardano MCP by Lido Nation & 2 Lovelaces

- Current proposer: 2 Lovelaces & Lido Nation
- Current requested budget: 339,900.00 ADA
- Triage matches: 7

#### Project Catalyst: cardano-dev-mcp: MCP for Devs of Cardano

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 85,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 2, score 0.224, shared terms: build, contracts, developer, documentation, mcp, smart, that
- Overlap evidence: Both proposals target Cardano MCP for developers. Historical proposal focused on 'CardanoPilot' with code generation and debugging; current proposal expands this to a full production suite of 54 tools including governance modules, though core AI assistant functionality remains the central theme.
- Funding evidence: Historical proposal was not approved and received no funding (85,000 ADA requested but unfunded). Current proposal is seeking new funding (339,900 ADA) for an expanded scope.
- Relationship evidence: Proposers are explicitly named as '2 Lovelaces & Lido Nation' in current proposal and 'p-lido-0198bc20-23cd-73f5-bda4-41f43f6c9928' (Lido Nation) in historical record.
- Review notes: While the core concept of a Cardano MCP AI assistant overlaps significantly with the historical proposal, the current work represents a substantial expansion into production-grade tooling and governance automation. The lack of prior funding means there is no direct precedent of completed work to avoid duplication, but the proposer's intent to build upon the same foundational idea warrants medium confidence overlap.
- Source: https://www.catalystexplorer.com/en/proposals/cardano-dev-mcp-mcp-for-devs-of-cardano-f14

#### Project Catalyst: Wolfram Cardano MCP Server: Smart Contracts & Catalyst

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 75,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 3, score 0.224, shared terms: build, contracts, governance, mcp, smart, tools
- Overlap evidence: Both proposals target Cardano MCP servers for AI-assisted development and governance. Historical proposal focused on 'Smart Contracts & Catalyst', while current expands to six modules including a specific '26 tool governance and DRep workbench built specifically for CIP 1694 participation'. Core concepts of MCP, smart contracts, and governance tools are shared.
- Funding evidence: Historical proposal was not approved and received no funding (75,000 ADA requested but unfunded). Current proposal is a new budget request (339,900 ADA) building upon the concept rather than re-funding the same specific project.
- Relationship evidence: Proposers are explicitly identified as '2 Lovelaces & Lido Nation' in current proposal and 'p-lido-1d9e38e1-ba8f-466a-9ad8-c9e508a8a7ac' (Lido Nation) in historical record.
- Review notes: The current proposal represents an evolution of the historical concept rather than a direct reuse. While the proposer is related and core themes overlap significantly (MCP, governance, smart contracts), the historical work was never funded and the current proposal introduces substantial new scope (CIP 1694 specific tools, expanded module count). The overlap is significant but not high confidence because the foundational work was not completed or funded.
- Source: https://www.catalystexplorer.com/en/proposals/wolfram-cardano-mcp-server-smart-contracts-catalyst-f14

#### Project Catalyst:  drep.space – MVP Validation of Governance Matching Tool

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 47,500.00 ADA)
- Proposer relationship: same
- Retrieval: rank 5, score 0.209, shared terms: active, alignment, drep, dreps, governance, participation, that, tool, tools, vision
- Overlap evidence: Both proposals focus on Cardano governance tools, specifically addressing DRep workload reduction. The current proposal's 'governance module' for CIP 1694 participation directly expands upon the historical 'drep.space' MVP which aimed to simplify governance via a 'Vision Quiz' and value alignment data.
- Funding evidence: Historical project was not funded (status: unfunded, previously_funded: no), so current funding does not represent direct reuse of prior capital but rather continuation of an unexecuted concept into production.
- Relationship evidence: Proposers are explicitly linked as '2 Lovelaces & Lido Nation' vs historical 'p-lido-295d710f-f949-4fce-b912-738ed813a6b7', with high proposer similarity score (0.222) and shared organizational context.
- Review notes: The proposal represents a significant evolution from the historical MVP validation phase to a production-grade toolset. While the core problem (DRep workload/governance clarity) and solution direction are highly aligned, the current work includes substantial new components (54 tools across 6 modules, specific CIP 1694 compliance focus) that exceed the scope of the original historical proposal, preventing a high-confidence overlap classification.
- Source: https://www.catalystexplorer.com/en/proposals/drepspace-mvp-validation-of-governance-matching-tool-f14

#### Project Catalyst: Empowering Cardano Governance: Project-Based Learning Modules for CIP-1694 Voltaire Participation

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 95,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 9, score 0.200, shared terms: 1694, cip, drep, governance, modules, participation, without
- Overlap evidence: Both proposals focus on CIP 1694 governance tools. Historical proposal focused on educational modules for DReps; current proposal builds production-grade AI tools including a governance module that automates DRep workload, representing a functional evolution of the same domain.
- Funding evidence: Historical proposal was not funded (status: unfunded, previously_funded: no). Current proposal budget is 339,900 ADA vs historical 95,000 ADA.
- Relationship evidence: Proposers are explicitly identified as '2 Lovelaces & Lido Nation' in current proposal and 'p-lido-01bc0dea...' / 'p-lido-d087d2d4...' (Lido Nation) in historical record.
- Review notes: Despite the historical proposal being unfunded and focused on education rather than production tools, the core subject matter (CIP 1694 governance support) and proposer identity indicate significant overlap. The current work represents a substantial upgrade from educational modules to automated AI tooling, but the foundational goal remains identical.
- Source: https://www.catalystexplorer.com/en/proposals/empowering-cardano-governance-project-based-learning-modules-for-cip-1694-voltaire-participation-f13

#### Project Catalyst: Cardano Explorer MCP(Model Context Protocol) Server

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: partial (no; 75,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 13, score 0.195, shared terms: blockchain, build, live, mcp, that
- Overlap evidence: Both proposals target Cardano MCP servers for AI agent integration. Historical work focused on 'Cardano Explorer data' with prebuilt actions, while current proposal expands to '54 production grade tools across six modules' including query and transaction building, representing a substantial but not total reuse of the foundational server concept.
- Funding evidence: Historical proposal was 'not_approved' and 'unfunded', meaning no prior funding exists for this specific work. The current proposal represents new funding for an expanded scope.
- Relationship evidence: Proposers are '2 Lovelaces & Lido Nation' vs historical 'p-lido-56224343-6a69-4c43-a4f2-dc1fc124c8dc', indicating a direct organizational link.
- Review notes: The historical proposal (F14) was rejected or never funded, so there is no direct precedent of funded overlap. However, the proposer relationship and the core technical objective (Cardano MCP server for AI agents) indicate significant conceptual reuse. The current proposal significantly expands the scope beyond the historical 'Explorer data' focus to include governance tools and broader transaction capabilities.
- Source: https://www.catalystexplorer.com/en/proposals/cardano-explorer-mcpmodel-context-protocol-server-f14

#### Project Catalyst: 1694.io - Open Governance Tooling & DRep Platform by Lido

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: partial (no; 200,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 17, score 0.189, shared terms: 1694, built, com, drep, equivalent, every, governance, lido, prototype, tooling
- Overlap evidence: Both proposals focus on CIP 1694 governance tooling. Historical proposal focused on 'making sense of' governance (explorer-like), while current proposal builds production-grade tools for DReps including sentiment analysis and forecasting, representing an evolution from prototype to full operational suite.
- Funding evidence: Historical funding was 200,000 ADA; current is 339,900 ADA. Historical status shows 'no' previously funded in the provided text context despite historical ID existence, suggesting a gap or specific proposal iteration not fully captured as funded in this review window.
- Relationship evidence: Proposers are explicitly linked as 'Lido Nation & 2 Lovelaces' vs historical 'p-lido-...' addresses; Lido is a known entity in Cardano governance.
- Review notes: The current proposal represents a substantial upgrade from the historical prototype work, moving from an exploratory governance understanding tool to a comprehensive AI-driven DRep workflow. The overlap is significant (governance focus) but distinct in execution and scope, fitting medium confidence rather than high confidence reuse.
- Source: https://www.catalystexplorer.com/en/proposals/1694io-open-governance-tooling-drep-platform-by-lido-f15

#### Project Catalyst: Boost Developer Efficiency: Cardano + Midnight Dev MCP Agent

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: partial (no; 75,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 21, score 0.187, shared terms: adoption, agent, build, developer, mcp, smart, that
- Overlap evidence: Both proposals target Cardano/Midnight developer efficiency via an MCP agent. Historical proposal focused on unified build/test/deploy for Cardano+Midnight; current proposal expands to 54 tools including governance (CIP 1694) and DRep workbench, representing a significant but not total expansion of the original scope.
- Funding evidence: Historical proposal was previously funded (75,000 ADA) but marked 'over_budget' and 'unfunded', suggesting prior execution or partial completion before this new proposal.
- Relationship evidence: Proposers are '2 Lovelaces & Lido Nation' vs historical 'p-lido-28a6ca18-33ed-4114-981d-fbcb28e17d43', indicating a direct organizational link.
- Review notes: The current proposal builds upon a previously proposed and partially funded agent framework. While the core concept of an AI MCP for Cardano/Midnight development is reused, the current proposal introduces substantial new functionality (governance/DRep tools) that was not in the historical scope, preventing a high-confidence overlap classification.
- Source: https://www.catalystexplorer.com/en/proposals/boost-developer-efficiency-cardano-midnight-dev-mcp-agent-f14

### Cardano Tooling DAO

- Current proposer: Cardano Tooling DAO LLC
- Current requested budget: 6,180,000.00 ADA
- Triage matches: none.

### Catalyze Africa: Building Scalable Projects from CATS 2026

- Current proposer: Wada Global
- Current requested budget: 989,901.00 ADA
- Triage matches: none.

### Civics Committee Governance Expert Led, Sustainable Education Program 

- Current proposer: Intersect Civics Committee
- Current requested budget: 442,900.00 ADA
- Triage matches: none.

### Clear signing of Cardano Top 5 dApps & Ledger Button integration

- Current proposer: Ledger Technologies SAS
- Current requested budget: 3,460,800.00 ADA
- Triage matches: none.

### Daedalus Wallet Maintenance and Improvements 2026–2027

- Current proposer: Se7en Labs
- Current requested budget: 1,112,400.00 ADA
- Triage matches: 1

#### Treasury Fund 1: Input Output Engineering Core Development Proposal (4of6)

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 5,137,599.00 ADA)
- Proposer relationship: same
- Retrieval: rank 21, score 0.182, shared terms: cip, development, ledger, nested, node, plutus, readiness, release, script, support
- Overlap evidence: Both proposals address Nested Transactions (CIP-0118) and PlutusV4 execution; however, the historical proposal focused on testnet readiness and conformance while the current proposal covers full mainnet hard fork preparation, Leios/Peras upgrades, and hardware wallet support.
- Funding evidence: The historical proposal was funded for core development milestones including Nested Transactions testing, whereas the current proposal requests broader maintenance and ecosystem expansion.
- Relationship evidence: Se7en Labs is the successor entity to Input Output Engineering (IOG), which historically managed Daedalus development.
- Review notes: While IOG (Se7en Labs) has historically funded Nested Transactions work, the specific scope of the current proposal extends beyond the previously funded testnet conformance phase to include full mainnet hard fork readiness and new hardware integrations. The overlap is significant but not total.
- Source: https://treasury.sundae.fi/budgets/9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619/project/UTXO-EC-0002-25-04

### Dano Finance: DeFi Kernel, American Options, and Orderbook SDK

- Current proposer: Dano Finance
- Current requested budget: 3,399,000.00 ADA
- Triage matches: 4

#### Project Catalyst: Cardano Global Orderbook

- Match confidence: medium
- Estimated current-work overlap: 35%
- Overlap type: significant_partial
- Previously proposed: True
- Previously funded relevance: none (no; 149,500.00 ADA)
- Proposer relationship: unknown
- Retrieval: rank 1, score 0.232, shared terms: composability, dexs, fragmented, global, liquidity, orderbook, orders, other, permissionless, protocols
- Overlap evidence: Historical work proposes a permissionless Cardano global orderbook. Current work includes a Global Orderbook SDK and orderbook trading primitive, alongside broader DeFi Kernel registry and American Options work.
- Funding evidence: Historical candidate is not marked funded in the archive.
- Relationship evidence: Historical row has only a Catalyst proposer id in the archive; no direct relationship evidence to Dano Finance.
- Review notes: Strong component overlap, but current proposal is broader than this single orderbook proposal.
- Source: https://www.catalystexplorer.com/en/proposals/cardano-global-orderbook-f15

#### Project Catalyst: Identify Dano DeFi Building Blocks

- Match confidence: medium
- Estimated current-work overlap: 35%
- Overlap type: significant_partial
- Previously proposed: True
- Previously funded relevance: partial (yes; 250,000.00 USD)
- Proposer relationship: possible
- Retrieval: rank 9, score 0.188, shared terms: dano, defi
- Overlap evidence: Historical title indicates Dano DeFi building blocks. Current proposal advances Dano Finance DeFi Kernel, orderbook, options, and SDK building blocks. Body text is unavailable in the archive, limiting certainty.
- Funding evidence: Historical proposal was approved for 250,000 USD; because body text is unavailable, funded relevance is treated as partial rather than full.
- Relationship evidence: Historical title contains Dano and DeFi building blocks; archive proposer identity is unknown, so relationship is likely but not proven by proposer metadata.
- Review notes: Important funded-prior-work candidate requiring manual source follow-up due missing body copy.
- Source: not captured

#### Project Catalyst: DeltaDeFi - Decentralized Financial Option Protocol on Cardano with eUTxO-native Efficient Order Book Model

- Match confidence: medium
- Estimated current-work overlap: 35%
- Overlap type: significant_partial
- Previously proposed: True
- Previously funded relevance: none (no; 219,633.00 ADA)
- Proposer relationship: unknown
- Retrieval: rank 11, score 0.187, shared terms: book, financial, integrations, management, markets, options, order, risk, trading
- Overlap evidence: Historical work proposes options and an eUTxO-native efficient order book model. Current proposal includes American Options and orderbook primitives, plus a broader Kernel registry and SDK.
- Funding evidence: Historical candidate was not approved.
- Relationship evidence: Historical row has only a Catalyst proposer id; no direct relationship evidence to Dano Finance.
- Review notes: Strong prior-proposed overlap for the options/orderbook component, but not previously funded.
- Source: https://www.catalystexplorer.com/en/proposals/deltadefi-decentralized-financial-option-protocol-on-cardano-with-eutxo-native-efficient-order-book-model-f10

#### Project Catalyst: American Options for Cardano DeFi

- Match confidence: medium
- Estimated current-work overlap: 30%
- Overlap type: significant_partial
- Previously proposed: True
- Previously funded relevance: none (no; 121,000.00 ADA)
- Proposer relationship: unknown
- Retrieval: rank 4, score 0.212, shared terms: american, defi, liquidity, markets, options, trading
- Overlap evidence: Historical work proposes decentralized American Options for Cardano DeFi. Current proposal explicitly includes American Options as one of its DeFi Kernel-compatible primitives.
- Funding evidence: Historical candidate is not marked funded in the archive.
- Relationship evidence: Historical row has only a Catalyst proposer id; no direct relationship evidence to Dano Finance.
- Review notes: Direct overlap with one major current deliverable, but not with the registry, orderbook SDK, or broader Kernel standard.
- Source: https://www.catalystexplorer.com/en/proposals/american-options-for-cardano-defi-f15

### DeltaDeFi: Cardano Flagship Exchange: ₳5,000,000 Treasury Loan with Perpetual Upside

- Current proposer: DeltaDeFi
- Current requested budget: 5,150,000.00 ADA
- Triage matches: 1

#### Project Catalyst: DeltaDeFi: Pioneering High-Frequency Trading on Cardano

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: partial (yes; 300,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 14, score 0.169, shared terms: book, deltadefi, matched, order, protocol, trading
- Overlap evidence: Both proposals address the core concept of building a high-frequency trading (HFT) exchange on Cardano. The historical work focused on the MVP and capability demonstration, while the current proposal focuses on scaling, hardening, and expanding an already live protocol with similar mechanics (order book matching). However, the current proposal explicitly cites objections to its previous draft and introduces new elements like a perpetual revenue share model and specific repayment terms not present in the historical text.
- Funding evidence: The historical funding was 300,000 ADA for MVP development. The current proposal seeks 5,150,000 ADA for scaling and hardening an existing live protocol. The historical status is 'complete' with leftover funding, indicating the initial phase concluded without full utilization or that the project evolved significantly.
- Relationship evidence: No direct link found between the historical proposer addresses (p-lido-*) and the current proposer 'DeltaDeFi'. The historical proposers appear to be Lido-related entities, whereas the current proposal is from a distinct entity.
- Review notes: The work overlap is moderate (medium confidence) because while both proposals support a DeltaDeFi HFT exchange on Cardano, they represent different stages of development (MVP vs. Scale-up). The current proposal appears to be from a different entity than the historical one, as there is no evidence linking 'DeltaDeFi' to the specific Lido-related proposer addresses in the historical record. The significant overlap lies in the underlying technology and market-making function, but the distinct proposers and evolved scope prevent a high-confidence classification of reuse.
- Source: https://www.catalystexplorer.com/en/proposals/deltadefi-pioneering-high-frequency-trading-on-cardano-f12

### Diversify Cardano treasury into prime, yield-bearing real-estate

- Current proposer: BRIDGE FUND
- Current requested budget: 65,405,000.00 ADA
- Triage matches: none.

### Dolos by TxPipe: Maintaining Cardano's Lightweight Data Node, Year 2

- Current proposer: TxPipe
- Current requested budget: 540,750.00 ADA
- Triage matches: 7

#### On-chain TreasuryWithdrawals: Withdraw ₳220,914 for Dolos: Sustaining a Lightweight Cardano Data Node

- Match confidence: high
- Estimated current-work overlap: 95%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 220,914.00 ADA)
- Proposer relationship: same
- Retrieval: rank 1, score 0.294, shared terms: access, across, actively, broader, chain, commits, compatibility, contract, contributions, data
- Overlap evidence: Both proposals fund the exact same project (Dolos: Lightweight Cardano Data Node) for identical core purposes (maintenance, updates, query response). The current proposal continues the initiative from the previous cycle with a different budget structure but identical scope of work (essential maintenance, community support, compatibility upgrades).
- Funding evidence: Current proposal requests 420,000 ADA; Historical withdrawal was 220,914 ADA. The current proposal explicitly states it continues the 'open source maintenance initiative funded through Intersect's treasury process in the previous cycle' and begins after the closure of the existing contract.
- Relationship evidence: Current proposer is TxPipe; Historical proposal was submitted by Intersect on behalf of the same vendor (TxPipe), explicitly stating 'This Treasury Withdrawal is submitted by Intersect on behalf of the vendor' and identifying TxPipe as the active member developing the project.
- Review notes: This is a direct continuation of previously funded work by the same vendor (TxPipe). The project scope, goals, and technical implementation remain identical. The current proposal represents an expansion of funding for the same ongoing maintenance task rather than new distinct work.
- Source: ipfs://bafkreihqhuiuwdjyukw4ul5obxz656ndyz5najokjhdw7mbdscskyaalfu

#### Project Catalyst: Dolos: Cardano “Data Node”

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 75,680.00 USD)
- Proposer relationship: different
- Retrieval: rank 2, score 0.248, shared terms: data, developer, dolos, fraction, ledger, node, nodes, performance, queries, resources
- Overlap evidence: Current proposal maintains Dolos as a lightweight Cardano data node with identical core functions (indexing ledger primitives, providing query interfaces like Mini Blockfrost and UTxO RPC). Historical funding covered development of this exact same narrow scope for keeping an updated ledger copy and replying to queries.
- Funding evidence: Current proposal requests $420k/year for maintenance; historical funding was $75.68k USD (approx $105k/year equivalent) for initial development. The work is non-additive as the current cycle continues the same project's lifecycle rather than creating new functionality.
- Relationship evidence: Different proposer entities (TxPipe vs p-lido-8116131a-47c4-46cc-a4da-093b4d549e7a); TxPipe explicitly references continuing the initiative funded by Intersect in the previous cycle.
- Review notes: This is a continuation grant for an existing open-source project. The proposer is different but explicitly acknowledges the prior funding cycle. The work overlap is high because the core product (Dolos data node) and its primary functions remain unchanged, with the current proposal focusing on maintenance and AI integration rather than new development.
- Source: https://www.catalystexplorer.com/en/proposals/dolos-cardano-data-node-f9

#### On-chain TreasuryWithdrawals: Withdraw ₳220,914 for UTxO RPC: Sustaining Cardano Blockchain Integration

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 220,914.00 ADA)
- Proposer relationship: same
- Retrieval: rank 4, score 0.218, shared terms: across, actively, chain, communication, contract, contributions, data, date, designed, developer
- Overlap evidence: The current proposal requests maintenance for 'UTxO RPC' (specifically mentioning Mini Blockfrost, UTxO RPC gRPC, etc.), which was the exact subject of the previously funded withdrawal. The historical text confirms TxPipe is developing this interface and that funding was requested to sustain it.
- Funding evidence: The current proposal continues the specific maintenance contract for UTxO RPC initiated in the historical action, expanding scope slightly but maintaining the core objective of sustaining the same open-source integration tool.
- Relationship evidence: TxPipe is explicitly named as the vendor in the historical proposal text and claims over 3 years of ecosystem development.
- Review notes: This is a direct continuation of a previously funded project by the same vendor. The work overlap is substantial as the current proposal maintains the exact same infrastructure (UTxO RPC) that was the subject of the historical funding, with only minor additions to scope (AI documentation). No new independent work is being proposed.
- Source: ipfs://bafkreibcranrq3y5eh7pcjuvq2tcmlapfw2pc7x3nazwp5lonx6docoayu

#### Project Catalyst: Dolos - A step closer to a Rust node - Phase-1 Validations

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 182,142.00 ADA)
- Proposer relationship: different
- Retrieval: rank 7, score 0.197, shared terms: data, development, dolos, full, node, resources, rust, source, would, year
- Overlap evidence: The current proposal focuses on maintaining Dolos (a lightweight Cardano data node in Rust), which was the exact subject of the historical Phase-1 Validations grant. The core work—maintaining the codebase, ensuring protocol compatibility, and providing query interfaces—is identical to the foundational work funded previously.
- Funding evidence: The current proposal requests 420,000 ADA for maintenance over 12 months, whereas the historical funding was 182,142 ADA. The increase reflects the transition from a development/validation phase (Phase 1) to a long-term operational maintenance phase.
- Relationship evidence: TxPipe is a distinct entity from the previously funded Lido addresses; however, TxPipe explicitly references Intersect's treasury process and continues the Dolos initiative established by the previous cycle.
- Review notes: The work is clearly continuous rather than additive; Dolos is the same project, and the scope has expanded from initial validation to full lifecycle maintenance including AI integration. While the proposers are different entities, the continuity of the project's existence under Cardano's treasury suggests a direct lineage of funding for the same underlying asset.
- Source: https://www.catalystexplorer.com/en/proposals/dolos-a-step-closer-to-a-rust-node-phase-1-validations-f10

#### Treasury Fund 1: TxPipe - Pallas, UTxO RPC, Dolos

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 662,742.00 ADA)
- Proposer relationship: same
- Retrieval: rank 14, score 0.178, shared terms: data, designed, dolos, improvements, integration, ledger, lightweight, maintenance, node, query
- Overlap evidence: Current proposal explicitly states continuation of 'open source maintenance initiative funded through Intersect's treasury process in the previous cycle.' Historical text details Dolos maintenance milestones which match current scope exactly. Current proposal adds AI documentation but core work is identical.
- Funding evidence: Previous funding was 662,742 ADA for a full year; current request is 540,750 ADA for 12 months, indicating continued support for the same project.
- Relationship evidence: TxPipe is the proposer in both cycles; historical funding address belongs to TxPipe ecosystem (Intersect); project name and scope are identical.
- Review notes: This is a renewal proposal for an existing active project. The work described is identical to the previously funded cycle (EC-0006-25 through EC-0010-25). The proposer is the same entity (TxPipe). The overlap is substantial as the current proposal is essentially a continuation of the previous contract with minor scope additions.
- Source: https://treasury.sundae.fi/budgets/9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619/project/EC-0006-25,EC-0007-25,EC-0010-25

#### Project Catalyst: gRPC ❤️ Cardano: A streaming API for Cardano using Dolos by TxPipe

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 177,082.00 ADA)
- Proposer relationship: same
- Retrieval: rank 24, score 0.171, shared terms: developer, dolos, friendly, grpc, node, protocol, provide, time, txpipe, unix
- Overlap evidence: The current proposal is a direct continuation of the historical project, shifting focus from building the gRPC API to maintaining the underlying Dolos node infrastructure that powers it. The scope includes upgrading compatibility with AI workflows and expanding query interfaces (Mini Blockfrost, UTxO RPC), which are logical extensions of the original streaming API work.
- Funding evidence: The current proposal requests 420,000 ADA for maintenance over 12 months, whereas the historical funding was 177,082 ADA. The previous funding covered development and initial deployment; the current funding covers long-term maintenance and expansion of the ecosystem tooling.
- Relationship evidence: TxPipe is the same entity as p-lido-8116131a-47c4-46cc-a4da-093b4d549e7a and p-lido-d259a3de-2cf0-4e2c-8f12-bb965a885de7; the proposal explicitly references continuing work from the previous cycle.
- Review notes: This is a clear case of project continuity rather than new work. The proposer is the same entity, and the work described is the operational phase following the development phase of the previously funded proposal. There is no meaningful overlap to exclude as it represents the natural lifecycle progression of the Dolos project.
- Source: https://www.catalystexplorer.com/en/proposals/grpc-cardano-a-streaming-api-for-cardano-using-dolos-by-txpipe-f11

#### Project Catalyst: Sundae Labs: Amaru Node Development Support - Rust Developer Contract

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 161,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 21, score 0.174, shared terms: contract, developer, development, ensuring, fund, maintenance, months, network, node, part
- Overlap evidence: Both proposals focus on maintaining Rust-based Cardano nodes (Dolos vs. Amaru) with similar scopes including dependency updates, performance improvements, bug fixing, and community support. The current proposal explicitly references the previous cycle's funding process for Dolos, indicating continuity in project type but not necessarily work content.
- Funding evidence: Previous funding was 161,000 ADA for 6 months; current request is 420,000 ADA for 12 months. The increase reflects the transition from a development-focused contract to a long-term maintenance role with expanded scope (AI integration).
- Relationship evidence: No direct organizational link found between TxPipe and the previously funded entities (p-lido-4d2b1c80-017d-4611-93b9-21c0ec788c2c, p-lido-ee292ca7-1181-40ea-a662-c59dcfba060f, p-lido-4ab60341-1b47-45e3-9b6d-4d5ccc144170). TxPipe is a distinct entity.
- Review notes: While the work types are similar (Rust node maintenance), the specific projects (Dolos vs. Amaru) and proposers differ significantly. The overlap is moderate due to shared technical domains rather than direct reuse of code or prior work outputs. The proposal appears to be a natural evolution of the ecosystem's need for lightweight node support, not a duplicate effort.
- Source: https://www.catalystexplorer.com/en/proposals/sundae-labs-amaru-node-development-support-rust-developer-contract-f13

### Ecosera: The End-to-End Clinical Research Ecosystem — From Trial Funding to Drug Approval on Cardano

- Current proposer: AxellaCoin
- Current requested budget: 1,390,508.00 ADA
- Triage matches: none.

### Enhance Swarm Treasury System with Open Social Governance

- Current proposer: Voltaire Swarm OÜ
- Current requested budget: 1,350,330.00 ADA
- Triage matches: none.

### Eryx: Zero-Knowledge Capabilities

- Current proposer: Eryx
- Current requested budget: 3,661,033.00 ADA
- Triage matches: 3

#### Project Catalyst: Cardano Privacy Layer: Zero-Knowledge Proof-Based Membership Verification and Anonymous Voting & Signaling (Phase 2)

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: partial (no; 300,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 1, score 0.256, shared terms: anonymous, applications, based, built, capabilities, common, ethereum, knowledge, layer, many
- Overlap evidence: Both proposals address Zero-Knowledge proof-based membership verification and anonymous voting/signaling. The historical proposal specifically targets the Semaphore protocol port, which is explicitly listed as Contribution #4 in the current proposal. However, the current proposal includes broader infrastructure components (PLONK verifier, RISC Zero zkVM adaptation) not present in the historical text.
- Funding evidence: Historical proposal was previously proposed but never funded (previously_funded_relevance: partial). Current budget is significantly higher than historical amount.
- Relationship evidence: Historical proposer names (p-lido-*) are distinct from current proposer (Eryx). Eryx is a 15-year-old company with independent experience in Cardano and ZK.
- Review notes: The current proposal builds upon the specific use case of anonymous signaling and voting defined in the historical proposal, adding a more comprehensive ZK framework. The overlap is significant regarding the Semaphore protocol implementation but does not constitute a duplicate or substantial reuse of the entire work scope.
- Source: https://www.catalystexplorer.com/en/proposals/cardano-privacy-layer-zero-knowledge-proof-based-membership-verification-and-anonymous-voting-signaling-phase-2-f12

#### Project Catalyst: Cardano Privacy Layer: Zero-Knowledge Proof-Based Membership Verification and Anonymous Voting & Signaling PoC.

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: partial (yes; 100,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 5, score 0.236, shared terms: anonymous, based, capabilities, ethereum, identity, knowledge, layer, many, membership, privacy
- Overlap evidence: Both proposals address Zero-Knowledge proof-based membership verification and anonymous voting/signaling. The current proposal explicitly builds upon the work of the historical proposal by implementing a PLONK verifier (Aiken), adapting RISC Zero zkVM, extending ZK libraries, and specifically implementing the Semaphore protocol for anonymous on-chain group signaling, which was the core focus of the historical PoC.
- Funding evidence: Historical funding was 100,000.00 ADA for a Proof of Concept (PoC). Current budget is 3,661,033.00 ADA for full framework implementation and production-grade tooling. The historical work covered the foundational concept and PoC execution, while the current proposal covers the substantial infrastructure development required to make ZK accessible on L1.
- Relationship evidence: Historical proposer names (p-lido-*) are distinct from current proposer (Eryx). Eryx is a 15-year-old company with experience in Cardano and ZK, while historical proposers appear to be project-specific entities or aliases.
- Review notes: The proposals share significant thematic overlap regarding privacy, membership verification, and anonymous signaling (Semaphore). However, the current proposal represents a major evolution from the historical PoC, moving from concept validation to building a comprehensive ZK framework. The proposers are not the same entity; Eryx is a distinct organization with deep experience in this domain, suggesting they may have built upon or independently developed similar concepts rather than simply reusing the exact historical deliverables. The overlap is significant but not total, as the current proposal adds new components (PLONK verifier in Aiken, RISC Zero integration) beyond the original PoC scope.
- Source: https://www.catalystexplorer.com/en/proposals/cardano-privacy-layer-zero-knowledge-proof-based-membership-verification-and-anonymous-voting-signaling-poc-f11

#### Project Catalyst: Incorporating Plonk into AK-381 Zero-Knowledge Library

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 100,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 18, score 0.194, shared terms: applications, dapps, developers, knowledge, library, plonk, zero
- Overlap evidence: Both proposals address the integration of PLONK into Cardano's ZK infrastructure (AK-381). The historical proposal specifically focused on incorporating PLONK into the library, while the current proposal expands this to include a PLONK verifier in Aiken, RISC Zero integration, and broader ZK framework development.
- Funding evidence: Historical proposal was not funded (previously_funded: no). Current proposal budget is significantly larger than historical amount.
- Relationship evidence: None detected. Historical proposer names are distinct from current proposer.
- Review notes: The current proposal represents a substantial evolution of the work initiated in the historical proposal. While the core technical objective (PLONK integration) overlaps significantly, the historical project was never funded and involved different proposers. The current proposal adds new dimensions (Aiken implementation, RISC Zero, Semaphore protocol) that go beyond the original scope, suggesting independent development rather than direct reuse of completed work.
- Source: https://www.catalystexplorer.com/en/proposals/incorporating-plonk-into-ak-381-zero-knowledge-library-f12

### Evolution SDK 2026. Hardening to v1.0, Modern DevEx, and the Agent Economy

- Current proposer: No.Witness Labs
- Current requested budget: 1,441,996.00 ADA
- Triage matches: 1

#### On-chain TreasuryWithdrawals: IO: Developer Experience Initiative

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 3,601,926.00 ADA)
- Proposer relationship: different
- Retrieval: rank 19, score 0.163, shared terms: actions, active, all, another, answer, any, built, chain, dapp, dashboard
- Overlap evidence: Both proposals address the same core problem: fragmented developer experience (DevX) and lack of tooling on Cardano. The current proposal aims to build a specific SDK ('Evolution SDK') with AI agent tooling, while the historical proposal aimed for a general 'Developer Experience Initiative' including bounties, starter CLIs, and smart contract libraries. The current proposal's focus on 'Modern DevEx' and 'Agent Economy' directly aligns with the historical goal of lowering barriers to entry and providing ready-to-use tools (OpenZeppelin-style contracts), representing a significant but not total overlap in scope.
- Funding evidence: The current proposal budget is 1,441,996 ADA against a previously funded amount of 3,601,926 ADA. The historical proposal was for a six-month program with milestone-based disbursement and independent third-party assurance, whereas the current proposal funds 12 months directly to 'make it production grade'.
- Relationship evidence: No direct name match found in historical proposer data; current proposer is 'No.Witness Labs' while historical text mentions collaboration with Intersect and TxPipe but does not explicitly name the funding recipient as No.Witness Labs.
- Review notes: The proposals share a strong thematic overlap regarding developer adoption and tooling standardization. However, the current proposal appears to be a more specific, implementation-focused follow-up (building a concrete SDK) rather than a direct continuation of the broader strategic initiative proposed historically. The lack of explicit proposer name continuity suggests different entities or teams are involved, though the goals remain consistent.
- Source: ipfs://QmUnSimkwuaXX357ugYxDkiUMzsKTYgcWvV74xWbiXUt3Y

### Formal Verification in Lean 4 and Blaster — Cardano Auditor Training Program 2026

- Current proposer: No.Witness Labs
- Current requested budget: 412,000.00 ADA
- Triage matches: 2

#### On-chain TreasuryWithdrawals: IO: Cardano High Assurance Technical Collaboration

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 13,078,578.00 ADA)
- Proposer relationship: same
- Retrieval: rank 1, score 0.187, shared terms: able, all, audit, auditing, auditor, blaster, catalyst, chain, checked, cohort
- Overlap evidence: The historical proposal (IO: Cardano High Assurance Technical Collaboration) funded the development of Blaster for DApp-level verification, a VS Code extension, and a Container Based Developer Environment (CBDE). The current proposal (Formal Verification in Lean 4 and Blaster) targets the exact same niche: training engineers to use Lean 4 + Blaster for Cardano EUTxO auditing. It relies on the 'team's existing formal verification lean4 course GitHub repository' which is the direct output of the historical workstream. The current proposal expands this into a curriculum and cohort program, but the underlying technical assets (Blaster integration, CBDE concepts, Lean 4 formal methods) are identical.
- Funding evidence: The historical funding of ~13M ADA supported the creation of the Blaster DApp verification toolchain and developer environment. The current proposal (~412k ADA) is a training program built upon these existing tools to create reusable curriculum and audit artifacts, representing a downstream application of the previously funded technical infrastructure.
- Relationship evidence: No.Witness Labs is explicitly named as a contributor in the historical proposal alongside Lantr, Harmonic Labs, and others; the current proposal states No.Witness Labs is 'the same entity currently delivering Catalyst Fund 14 milestone by milestone'.
- Review notes: The current proposal represents a direct continuation and educational expansion of the work initiated in the historical proposal. While the historical proposal focused on building the toolchain (Blaster extension, CBDE), the current proposal focuses on training engineers to use that specific toolchain. The overlap is high because the current proposal cannot exist without the technical foundation laid by the previous one, and the proposer is the same entity involved in both.
- Source: ipfs://QmfM3VRtGvpmxTDYrgGJoPSLW41SiNyeazfjusg98jrATS

#### Project Catalyst: Empowering Global Cardano Growth with Lean Education

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 60,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 3, score 0.182, shared terms: formal, lacks, lean, verification
- Overlap evidence: Both proposals target formal verification education using Lean 4 for Cardano; current proposal expands on the historical concept with a specific curriculum, cohorts, and open-source artifacts under MIT license.
- Funding evidence: Historical proposal (F14) was not funded ($60k ADA); current proposal seeks $412k ADA for a more structured training program.
- Relationship evidence: Different legal entities (No.Witness Labs LLC vs p-lido-323e1081-182f-4a12-9199-65ba83b6b7fe); historical proposal was unfunded and not approved.
- Review notes: The current proposal represents an evolution of the historical concept, moving from general education to a specific cohort-based training program with tangible open-source outputs. While the core idea (Lean verification education) is reused, the proposer is different and the previous work was not funded, indicating medium confidence overlap rather than high confidence reuse.
- Source: https://www.catalystexplorer.com/en/proposals/empowering-global-cardano-growth-with-lean-education-f14

### Full Integration of CIP-113 with Clear Signing across Ledger Products

- Current proposer: Ledger Technologies SAS
- Current requested budget: 92,700.00 ADA
- Triage matches: none.

### GOV.EXE by TxPipe & gf Consulting Group: Public Project Execution Integrity, Pilot in Argentina

- Current proposer: TxPipe
- Current requested budget: 3,006,828.00 ADA
- Triage matches: none.

### Governance Coalition: Governance Prototype and RFP Program

- Current proposer: Voltaire Swarm
- Current requested budget: 2,664,095.00 ADA
- Triage matches: none.

### Hardware Wallet Maintenance 2026

- Current proposer: VacuumLabs 
- Current requested budget: 1,310,960.00 ADA
- Triage matches: 2

#### Treasury Fund 1: VacuumLabs - Hardware Wallets Maintenance & Ledger App Rewrite

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 724,800.00 ADA)
- Proposer relationship: different
- Retrieval: rank 1, score 0.326, shared terms: app, audit, breaking, changes, core, firmware, flows, hardware, integration, ledger
- Overlap evidence: identical scope of Ledger/Trezor firmware maintenance, breaking change handling, and audit requirements; current proposal is a continuity extension of the paused historical project
- Funding evidence: historical funding of 724,800 ADA for identical work now requested again as 1,310,960 ADA
- Relationship evidence: different wallet addresses indicating distinct entities
- Review notes: The current proposal appears to be a renewal or continuation of previously funded work by a different entity. The scope is nearly identical (Ledger/Trezor firmware maintenance, breaking changes, audits), but the proposer addresses are different, suggesting potential re-funding of the same work rather than new development.
- Source: https://treasury.sundae.fi/budgets/9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619/project/EC-0011-25 EC-0005-25

#### On-chain TreasuryWithdrawals: Withdraw ₳424,800 for Hardware Wallets Maintenance administered by Intersect

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 424,800.00 ADA)
- Proposer relationship: different
- Retrieval: rank 2, score 0.270, shared terms: assurance, audit, audits, breaking, changes, cli, core, developer, firmware, funding
- Overlap evidence: Both proposals fund identical services: Ledger/Trezor firmware updates, cardano hw cli maintenance, developer support for Keystone, and external audits. The current proposal is a continuity extension for the same proven access layer.
- Funding evidence: Historical withdrawal of 424,800 ADA funded the exact same scope; current proposal requests 1,310,960 ADA for 12 months of production maintenance of the same components.
- Relationship evidence: VacuumLabs is the vendor and recipient in both proposals; Intersect administers funding on behalf of CDH. VacuumLabs developed integrations since 2018.
- Review notes: The current proposal is a direct continuation of previously funded work by the same vendor (VacuumLabs). The scope is identical (Ledger/Trezor firmware updates, CLI maintenance, audits), and the proposer relationship is confirmed through vendor identity. This represents high-confidence overlap where the new funding replaces or extends the historical mandate rather than introducing new work.
- Source: ipfs://bafkreicmz5a6ylplflowjdj7vjzp6glt45k2r6mnhwlmzq7kjkl3fvuzeu

### High-performance Rust Ogmios Client

- Current proposer: WingRiders Ltd.
- Current requested budget: 545,694.00 ADA
- Triage matches: 1

#### Project Catalyst: SIDAN | MeshJS - Advance Cardano SDK in Rust

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 200,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 19, score 0.185, shared terms: all, backend, building, developer, developers, efficient, implementation, low, rust
- Overlap evidence: Both proposals target building a Rust-based Cardano SDK/client for backend interoperability. The historical project explicitly built upon previous funded pilot research to create a 'developer ready SDK', while the current proposal aims to implement a 'robust high performance Ogmios client library' in Rust, covering similar functional areas like chain synchronization and transaction submission.
- Funding evidence: Historical funding of 200,000.00 ADA was approved for advancing the Cardano SDK in Rust, establishing foundational work that the current proposal builds upon to create a production-grade Ogmios client.
- Relationship evidence: No direct organizational link found between WingRiders Ltd. and the previously funded Lido entities; proposer similarity score is low (0.113).
- Review notes: The current proposal represents an evolution of the previously funded work rather than a duplicate. While the core technology (Rust SDK for Cardano RPC) is highly relevant and overlaps significantly with the historical project's goals, the specific implementation target has shifted from a general 'Cardano SDK' to a specialized 'Ogmios Client'. The proposer appears distinct from the previous funding recipients.
- Source: https://www.catalystexplorer.com/en/proposals/sidan-meshjs-advance-cardano-sdk-in-rust-f12

### Hub-Network Liquidity: A Protocol for Revenue-based Finance at Network Scale

- Current proposer: Prisma
- Current requested budget: 1,524,400.00 ADA
- Triage matches: none.

### Indigo Innovation Proposal: V2030RS, Tokenized RWA, BTC-Fi & Privacy

- Current proposer: Indigo Foundation
- Current requested budget: 3,965,500.00 ADA
- Triage matches: 1

#### Project Catalyst: Institutional-Grade Layer-2 for Bitcoin DeFi on Cardano, in collaboration with BitcoinOS, Tesseract and More

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 852,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 9, score 0.190, shared terms: bitcoin, defi, grade, institutional, liquidity
- Overlap evidence: Both proposals address building an institutional-grade Layer 2 for Bitcoin DeFi on Cardano to solve liquidity and scalability issues. The historical proposal explicitly mentions collaboration with BitcoinOS and Tesseract, while the current proposal focuses on iUSDt and partnerchain ecosystems. Core technical goals (scalability, speed, cost efficiency) are identical.
- Funding evidence: Historical funding of 852,000 ADA was approved for a similar project structure. The current proposal budget is 3,965,500 ADA, suggesting an expansion or evolution of the original concept rather than a complete restart.
- Relationship evidence: Historical proposer entities (p-lido-0d5ad802..., p-lido-be3b70fa...) are distinct from current proposer (Indigo Foundation). While both involve Bitcoin DeFi infrastructure on Cardano, the specific entities and organizational structures differ.
- Review notes: The proposals represent an evolution of the same core technical challenge (Bitcoin DeFi L2 on Cardano). While the proposer has changed from Lido-related entities to Indigo Foundation, the work is substantially overlapping in intent and scope. The current proposal appears to be a continuation or rebranding of the previously funded F13 project, potentially incorporating new partners like Tesseract and expanding into tokenized RWA.
- Source: https://www.catalystexplorer.com/en/proposals/institutional-grade-layer-2-for-bitcoin-defi-on-cardano-in-collaboration-with-bitcoinos-tesseract-and-more-f13

### Infrastructure for Quality Certification and Traceability in the Floriculture Industry

- Current proposer: David Tacuri
- Current requested budget: 653,947.00 ADA
- Triage matches: none.

### Innovation & Growth DAO

- Current proposer: Innovation & Growth DAO
- Current requested budget: 14,304,640.00 ADA
- Triage matches: 1

#### Project Catalyst: DRep DAO Platform

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: significant_partial
- Previously proposed: True
- Previously funded relevance: none (yes; 4,800.00 ADA)
- Proposer relationship: different
- Retrieval: rank 12, score 0.189, shared terms: dao, drep, dreps, funding, funds, process, proposals, requests, small, too
- Overlap evidence: Both proposals address the need for streamlined funding mechanisms for small teams/projects that are too early or small for direct Treasury requests. The core concept of a DAO-based platform to handle smaller funding rounds is shared.
- Funding evidence: Historical proposal sought general access to lower funds via DRep DAO; current proposal proposes a specific structured mechanism with caps, skin-in-the-game, and milestone disbursement. Historical amount (4,800 ADA) is negligible compared to current budget (14M ADA).
- Relationship evidence: Different proposers; Historical proposer is a specific Lido DRep entity, while current proposer is the Innovation & Growth DAO.
- Review notes: The proposals share a thematic focus on improving accessibility for small funding requests but differ significantly in structure and scale. The historical proposal was a conceptual request for a platform, while the current proposal outlines a specific operational framework. The overlap is significant in concept but not in execution or substance.
- Source: https://www.catalystexplorer.com/en/proposals/drep-dao-platform-f14

### Integration of Cardano into the Houdiniswap Aggregator

- Current proposer: Houdiniswap
- Current requested budget: 1,311,190.00 ADA
- Triage matches: none.

### Intersect Technical Steering Committee Support

- Current proposer: Intersect Technical Steering Committee
- Current requested budget: 1,193,000.00 ADA
- Triage matches: 2

#### Treasury Fund 1: Input Output Engineering Core Development Proposal (6of6)

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: significant_partial
- Previously proposed: True
- Previously funded relevance: partial (yes; 33,664,800.00 ADA)
- Proposer relationship: same
- Retrieval: rank 1, score 0.238, shared terms: committee, included, independent, infrastructure, intersect, protocol, provide, reports, security, support
- Overlap evidence: The historical proposal funded monthly maintenance, independent audits, and security assurance. The current proposal funds technical governance infrastructure including a Parameter Committee, CIP editors, Hard Fork Working Group, and an independent technical review programme. While both involve Intersect managing protocol stability and security, the specific deliverables differ: the historical focus was on ongoing maintenance and audit reports, whereas the current focus is on establishing governance structures and future-proofing protocols.
- Funding evidence: Historical funding of ~33.6M ADA vs current request of ~1.2M ADA; historical status 'contracted' vs current 'proposed'.
- Relationship evidence: Both proposals are managed by Intersect (Input Output Engineering), with the current proposal explicitly contingent on the approval of the historical MBO budget.
- Review notes: The proposals represent a shift from operational maintenance (historical) to structural governance setup (current). The overlap is significant in terms of organizational function and security focus but distinct in specific deliverables, warranting medium confidence rather than high.
- Source: https://treasury.sundae.fi/budgets/9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619/project/UTXO-EC-0002-25-06

#### Treasury Fund 1: Intersect MBO - A member-based organization for the Cardano ecosystem

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: significant_partial
- Previously proposed: True
- Previously funded relevance: none (yes; 15,750,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 23, score 0.173, shared terms: activities, all, budget, committee, dreps, ensuring, function, funded, governance, groups
- Overlap evidence: The current proposal focuses on specific technical governance activities (Parameter Committee, CIP editors, Hard Fork Working Group) and independent review. The historical proposal covered broader administrative and infrastructure stewardship including 'Maintain and govern open source Cardano node repositories', 'Coordinate and release upgrades', and support for '8 committees and 30+ working groups'. While the current proposal is narrower in scope (technical governance vs general admin/infrastructure), it represents a core subset of the historical mandate, specifically the committee coordination and upgrade coordination aspects.
- Funding evidence: The historical funding was $15,750,000 ADA for a multi-year operational stream including committee elections and roadmap submissions. The current proposal is $1,193,000 ADA for 12 months of technical governance support. The current work is not discretionary but foundational to the ecosystem's technical direction, similar to the historical goal of providing 'stability and continuity across key engineering practices'.
- Relationship evidence: Proposer is the Intersect Technical Steering Committee (TSC), which operates under the Intersect MBO framework. The historical proposal explicitly states Intersect will 'Execute administrator role for proposals funded by Cardano treasury' and provide support through 'members and committees', directly mirroring the current proposal's request for TSC support.
- Review notes: The overlap is medium because while the proposer is identical and the mission (Cardano governance) is shared, the specific deliverables differ: the historical proposal was broader (admin, node repo maintenance, general committee support), whereas the current proposal is more specialized (technical steering, parameter committees, hard forks). The historical proposal's scope included 'committee elections' and 'roadmap submission', which are distinct from the current proposal's focus on 'technical direction' and 'independent review'. However, the core function of managing technical committees and ensuring safe upgrades represents a significant portion of the historical work.
- Source: https://treasury.sundae.fi/budgets/9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619/project/EG-0002-25

### Intersect: Governance coordination and technical stewardship for the Cardano ecosystem

- Current proposer: IntersectMBO
- Current requested budget: 25,400,000.00 ADA
- Triage matches: 4

#### Treasury Fund 1: Intersect MBO - A member-based organization for the Cardano ecosystem

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 15,750,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 1, score 0.275, shared terms: based, chain, committees, continuity, coordination, core, function, governance, groups, haskell
- Overlap evidence: Current proposal explicitly describes the evolution of Intersect's core operating model which mirrors the previously funded scope: administrator role for treasury proposals, on-chain governance support, facilitation of Vision/Roadmap/Budget proposals, stewardship of Haskell repositories, coordination of upgrades, and management of committees/working groups.
- Funding evidence: Historical funding (15.75M ADA) covered the exact administrative and technical streams now being funded (25.4M ADA), with the current proposal reducing scope from a previous year's $7.875M ask while retaining critical continuity functions.
- Relationship evidence: Same entity (Intersect MBO) transitioning from a funded contract to an ongoing operational model; proposer address matches historical recipient.
- Review notes: The proposal represents a continuation of the Intersect MBO contract rather than new work. The historical funding covered the same administrative and technical stewardship roles (node repo governance, upgrade coordination, committee management). The current proposal is an evolution of this existing operational model, not a distinct project.
- Source: https://treasury.sundae.fi/budgets/9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619/project/EG-0002-25

#### On-chain TreasuryWithdrawals: Withdraw ₳15,750,000 for a MBO for the Cardano ecosystem: Intersect

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: full (yes; 15,750,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 2, score 0.267, shared terms: address, backbone, based, capacity, chain, committees, continuity, coordinating, coordination, core
- Overlap evidence: Both proposals describe Intersect's role as a neutral coordination layer for Cardano governance and technical stewardship. The current proposal continues the operational model of the historical one, expanding slightly in scope to include AI advancements while maintaining core responsibilities like Haskell repository stewardship, upgrade coordination (Chang/Plomin), incident response, and committee support.
- Funding evidence: Historical funding was ₳15,750,000 for June 2025-June 2026; current funding is ₳25,400,000 for June 2026-June 2027. The increase reflects the proposal's evolution to address a more mature ecosystem and new technical challenges (AI), but the fundamental operational mandate remains identical.
- Relationship evidence: Proposer name 'IntersectMBO' matches the historical recipient 'Intersect'; both proposals explicitly fund the same Member Based Organization (MBO) for identical core functions.
- Review notes: This is a direct continuation of the Intersect MBO funding cycle. The work described is not new but represents an expansion of the previously funded operational model. There is no indication of unrelated work or different entities; the overlap covers nearly all aspects of the current proposal's scope.
- Source: ipfs://bafkreidy6xsjjpdccodhiurbdcvtcf5tqzkyfgx3ruuhso2ijjuovycuny

#### On-chain TreasuryWithdrawals: IO & Ensurable Systems: Cardano Maintenance Initiative

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 62,134,630.00 ADA)
- Proposer relationship: same
- Retrieval: rank 4, score 0.200, shared terms: 2027, address, ask, based, bug, capacity, chain, confidence, continuity, core
- Overlap evidence: Both proposals fund continuous operational support for Cardano's core infrastructure. The historical proposal explicitly lists 'Full Node release process (integration, build, test, release, documentation, communications), L1/L2/L3 incident management' and 'Cardano API/CLI maintenance', which directly map to the current proposal's 'incident response, and release coordination required to help keep Cardano secure, reliable, and operationally resilient.' The historical text mentions 'CI/CD system maintenance' and 'disaster recovery per CIP 135,' aligning with the current focus on 'technical stewardship' and 'operational resilience.'
- Funding evidence: The historical proposal (₳62,134,630) funded a comprehensive maintenance envelope covering bug fixing, CI/CD, monitoring, documentation, open source support, performance analysis, QA, release management, and component maintenance. The current proposal (₳25,400,000) funds the same core operating model but with a reduced budget, focusing on the critical continuity functions previously covered.
- Relationship evidence: IntersectMBO is the proposer for both; Intersect administers funds in the historical proposal and operates the core maintenance function described.
- Review notes: The current proposal represents a continuation of the historical 'IO & Ensurable Systems' initiative by Intersect. The work is not additive; rather, it is a scaled-down iteration of the same operational stewardship function. The high overlap in specific technical responsibilities (incident response, release coordination, CI/CD, monitoring) confirms that the current proposal covers a significant portion of previously funded work.
- Source: ipfs://QmZMFAZvCxW6HpRC1EKzNcensJv9N89yzKPn7uRTTJdTpx

#### On-chain TreasuryWithdrawals: Withdraw ₳5,885,000 for OSC Budget Proposal - Paid Open Source Model...

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 5,885,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 12, score 0.168, shared terms: address, advancements, based, bounties, bug, chain, confidence, coordinated, coordinating, core
- Overlap evidence: Both proposals address the core mission of funding and sustaining Cardano's open source ecosystem. The historical proposal introduced a 'Paid Open Source Model' with specific components like a 'Maintainer Retainer Program', 'Bug bounty and security initiatives', and 'Developer advocacy'. The current proposal covers these exact functions under 'technical stewardship', 'incident response', 'release coordination', and 'security initiatives such as bug bounties'. While the historical focus was specifically on the OSC budget model, the current proposal expands this into a broader operational layer for the ecosystem, indicating substantial functional reuse rather than identical work.
- Funding evidence: The historical funding of ₳5,885,000 ADA supported the Paid Open Source Model. The current proposal requests ₳25,400,000 ADA to fund a more mature and expanded operational model that includes the previously funded functions plus additional governance coordination and incident response capabilities.
- Relationship evidence: The current proposal is submitted by IntersectMBO, which explicitly states in the historical text that it acts 'on behalf of the Open Source Committee' (OSC). The historical proposal was also submitted by Intersect on behalf of OSC.
- Review notes: The overlap is medium confidence because while the core mission (funding open source maintenance and security) is identical and the proposer is the same entity acting for the same committee, the current proposal represents an evolution of the previous work into a broader operational framework rather than a direct repeat. The historical text confirms Intersect's role in executing the OSC budget, which aligns directly with the current 'technical stewardship' remit.
- Source: ipfs://bafkreiedjhlwerulq5qg5tku2qqremf2cf2dguxvktttnjddei3fxct37a

### Libertum: Institution-Grade Participation Infrastructure for Cardano Real-World Assets

- Current proposer: Libertum
- Current requested budget: 2,193,900.00 ADA
- Triage matches: 2

#### Project Catalyst: Cardano’s $10T Institutional RWA Tokenization Infrastructure

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (no; 750,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 1, score 0.302, shared terms: 113, assets, cip, compliance, designed, grade, growth, infrastructure, institutional, libertum
- Overlap evidence: Both proposals target identical goals: institution-grade RWA tokenization infrastructure on Cardano using CIP 113 for compliance, permissions management, and regulated issuance. The historical text identifies Libertum as the entity building this infrastructure, while the current proposal details Libertum's existing operational status ($115M tokenized assets) and plans to accelerate this same infrastructure.
- Funding evidence: Historical funding was $750,000 ADA; current budget is $2,193,900 ADA. The historical proposal explicitly names Libertum as the builder, indicating the work was previously proposed and funded by the same entity.
- Relationship evidence: Libertum is explicitly named as the builder in both proposals; historical text states 'Libertum will build Cardano's first fully compliant and institutional grade tokenization infrastructure utilizing CIP 113', matching current proposal's focus on Libertum's operational implementation of CIP 113.
- Review notes: The current proposal represents a continuation and expansion of the previously funded F15 project. The core technical scope (CIP 113 compliance infrastructure for RWAs) and the proposer (Libertum) are identical. The historical text confirms Libertum was the intended builder, making this a clear case of previously funded work being re-proposed with increased budget rather than new independent work.
- Source: https://www.catalystexplorer.com/en/proposals/cardanos-10t-institutional-rwa-tokenization-infrastructure-f15

#### Project Catalyst: Cardano Institutional UX Stack: Compliance & BTC-Ready DeFi

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: partial (no; 825,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 3, score 0.226, shared terms: across, adoption, compliance, flows, grade, including, institutional, ready, regulated, reusable
- Overlap evidence: Both proposals address institutional compliance and UX for Cardano DeFi. Historical F14 focused on modular UX, identity frameworks, and BTC-ready flows. Current Libertum proposal focuses on CIP 113 programmable compliance infrastructure, regulated issuance, and operational workflows. The core concept of building reusable institutional-grade compliance/UX infrastructure is shared, but the specific implementation (CIP 113 vs general UX stack) and target scope differ.
- Funding evidence: Historical proposal was previously funded (825,000 ADA) but marked as unfunded in this context due to over-budget status. Current proposal budget is 2,193,900 ADA.
- Relationship evidence: Different entities: Current proposer is 'Libertum', historical proposer is 'p-lido-9e49d751-dbf0-4efe-8a03-856d208cd3d9' (Lido).
- Review notes: The current proposal builds upon the conceptual foundation laid by F14 regarding institutional compliance and UX, moving from a general framework to specific CIP 113 implementation. However, the proposers are unrelated (Libertum vs Lido), suggesting independent development rather than direct reuse of code or assets. The overlap is significant in concept but not in execution.
- Source: https://www.catalystexplorer.com/en/proposals/cardano-institutional-ux-stack-compliance-btc-ready-defi-f14

### Marlowe V2

- Current proposer: Simon Thompson
- Current requested budget: 1,802,500.00 ADA
- Triage matches: 5

#### Project Catalyst: Marlowe 2025: Marlowe V2

- Match confidence: high
- Estimated current-work overlap: 95%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (no; 150,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 1, score 0.362, shared terms: core, design, language, marlowe, proposals, prototype
- Overlap evidence: Both proposals address identical core objectives: modernizing Marlowe V2 based on community feedback, involving developers and users in design, and focusing on the same deliverables (on-chain validator, off-chain runtime, tools). The historical text explicitly states 'design its successor, Marlowe V2', while the current proposal details 'modernise and update Marlowe to face the challenge of delivering Cardano DeFi' with identical scope components.
- Funding evidence: Historical funding was 150,000.00 ADA; current budget is 1,802,500.00 ADA. Historical status 'unfunded' and 'over_budget' confirms no prior execution of this specific work.
- Relationship evidence: Historical proposer IDs (p-lido-...) differ from current proposer (Simon Thompson); historical status is 'unfunded' and 'over_budget', indicating the proposal was not executed.
- Review notes: Despite the historical proposal being unfunded and over budget, it represents a direct conceptual predecessor to the current proposal. The current proposer (Simon Thompson) is not the same as the historical recipients (Lido-related entities), but the work itself is nearly identical in scope and intent, suggesting the current proposal is a re-submission or continuation of the original vision rather than new independent work.
- Source: https://www.catalystexplorer.com/en/proposals/marlowe-2025-marlowe-v2-f13

#### Project Catalyst: Marlowe 2025

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (no; 500,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 2, score 0.306, shared terms: core, make, marlowe, runtime
- Overlap evidence: Both proposals address Marlowe modernization, simplification, extension for oracles/micropayments, runtime optimization, and on-chain/off-chain infrastructure. Historical text mentions 'consolidate and extend Marlowe to make it a first choice', directly aligning with the current proposal's goal to 'modernise and update Marlowe'.
- Funding evidence: Historical proposal was unfunded but over budget, suggesting scope expansion or lack of approval rather than completed work; however, the conceptual framework and technical direction are identical.
- Relationship evidence: Historical proposer IDs (p-lido-*) match the domain of the current proposal's core team context; historical text explicitly references 'core maintainers' and 'Marlowe V2', indicating continuity in leadership.
- Review notes: The current proposal is a direct continuation of the historical Marlowe project. The core team appears to be the same (or closely related), and the proposed work covers nearly all aspects mentioned in the previous proposal, including runtime, on-chain validation, and tooling. The lack of prior funding does not negate the overlap in scope or intent.
- Source: https://www.catalystexplorer.com/en/proposals/marlowe-2025-f12

#### Project Catalyst: Wolfram Marlowe Smart Contract Execution

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 294,857.00 ADA)
- Proposer relationship: different
- Retrieval: rank 12, score 0.195, shared terms: contract, financial, marlowe, smart, solution, support, things, time
- Overlap evidence: current proposal explicitly modernizes Marlowe V2.0 based on the same DSL architecture; historical funding covered real-time pricing and autonomous execution which are core components of the current platform scope
- Funding evidence: historical funding of 294,857 ADA supported foundational execution logic; current proposal requests 1,802,500 ADA for modernization including validator, runtime, and L2 feasibility study
- Relationship evidence: different proposer entities (Simon Thompson vs p-lido addresses)
- Review notes: While proposers are different, the work represents a direct evolution of the same Marlowe ecosystem. The historical project established the core financial contract execution mechanism (pricing + autonomous logic), which the current proposal aims to modernize and expand into V2.0/V2.1. Given that no other technology on Cardano has fully cracked this domain, the overlap is substantial rather than adjacent.
- Source: https://www.catalystexplorer.com/en/proposals/wolfram-marlowe-smart-contract-execution-f11

#### Project Catalyst: Marlowe Runtime SDKs

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 154,286.00 ADA)
- Proposer relationship: different
- Retrieval: rank 5, score 0.252, shared terms: adoption, blockchain, contracts, developers, financial, marlowe, runtime
- Overlap evidence: Current proposal focuses on Marlowe V2.0 platform including validator, runtime, and tools for financial contracts. Historical funding covered only the SDKs for the Marlowe Runtime backend. While both address Marlowe infrastructure, the current scope is broader (platform/validator) and the historical scope was narrower (SDKs), representing significant but not total overlap.
- Funding evidence: Historical funding of 154,286 ADA for SDKs vs current request of 1,802,500 ADA for full platform modernization; historical work does not cover the validator or V2.0 tooling requested now.
- Relationship evidence: proposers are distinct entities (Simon Thompson vs p-lido addresses); no shared names or organizational affiliations found.
- Review notes: The proposal builds upon Marlowe infrastructure but represents a distinct evolution from the previously funded SDK-only project. The proposer is unrelated to the previous recipients (Lido addresses). Overlap is significant regarding the core runtime concept but not in terms of specific deliverables or scope.
- Source: https://www.catalystexplorer.com/en/proposals/marlowe-runtime-sdks-f10

#### Project Catalyst: Marlowe for Financial Markets

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 14,000.00 USD)
- Proposer relationship: different
- Retrieval: rank 6, score 0.228, shared terms: defi, financial, full, haskell, marlowe, plutus
- Overlap evidence: identical_core_objective_of_enabling_financial_contract_development_on_cardano_via_marlowe_dsl
- Funding evidence: current_budget_1802500_vs_previous_14000_usd_indicates_major_scale_increase_for_new_version
- Relationship evidence: different_entity_addresses_and_names
- Review notes: While the core vision of Marlowe as a DSL for financial contracts remains consistent, the current proposal represents a substantial modernization effort (V2.0) compared to the initial pilot/foundation work funded previously. The proposer is unrelated, and the budget increase suggests new scope rather than simple continuation.
- Source: https://www.catalystexplorer.com/en/proposals/marlowe-for-financial-markets-f8

### Mithril Protocol

- Current proposer: Teragone Factory
- Current requested budget: 3,739,559.00 ADA
- Triage matches: 3

#### Treasury Fund 1: Input Output Engineering Core Development Proposal (3of6)

- Match confidence: high
- Estimated current-work overlap: 95%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 3,765,286.00 ADA)
- Proposer relationship: different
- Retrieval: rank 8, score 0.167, shared terms: chain, mithril, node, protocol
- Overlap evidence: Current proposal describes Mithril Protocol's core function of stake-based threshold multi-signature state verification. Historical proposal explicitly details the completion and delivery of Mithril ZK Proofs Project milestones (MS8.5-MS8.7), which constitute the exact same technical deliverables described in the current text.
- Funding evidence: Current budget (3,739,559.00 ADA) is nearly identical to historical funding (3,765,286.00 ADA), indicating a continuation of the same project scope rather than new work.
- Relationship evidence: Teragone Factory is a distinct entity from Input Output Engineering; no direct organizational link indicated.
- Review notes: The current proposal appears to be a re-submission or continuation of the previously funded Mithril ZK Proofs Project by Input Output Engineering. The proposer Teragone Factory is unrelated, suggesting this may be an attempt to re-fund completed or paused work under a different entity name, which warrants conservative scrutiny regarding the necessity of new funding.
- Source: https://treasury.sundae.fi/budgets/9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619/project/UTXO-EC-0002-25-03

#### Project Catalyst: zkFold x Anastasia Labs: ZK Bridge using Mithril

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: partial (yes; 345,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 4, score 0.190, shared terms: centralized, chain, enabling, mithril, multi, signatures, using, verify
- Overlap evidence: Both proposals utilize Mithril Protocol for state verification, but the historical proposal focused on a ZK bridge between isomorphic blockchains while the current proposal addresses general blockchain state access and verification infrastructure.
- Funding evidence: Historical funding of 345,000.00 ADA was approved for a specific ZK bridge use case; current proposal requests 3,739,559.00 ADA for broader infrastructure challenges.
- Relationship evidence: Different proposers identified (Teragone Factory vs p-lido-1b34013d-fc54-4847-aa76-7e457b2de54c) with low proposer similarity score of 0.169.
- Review notes: The work is not identical but represents significant reuse of the Mithril technology in a different application context (general state verification vs cross-chain bridging). The proposers are unrelated entities, indicating independent adoption of the same underlying protocol rather than direct project continuation.
- Source: https://www.catalystexplorer.com/en/proposals/zkfold-x-anastasia-labs-zk-bridge-using-mithril-f12

#### Treasury Fund 1: Harmonic Laboratories: Gerolamo - Cardano Node in typescript

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: partial (yes; 578,571.00 ADA)
- Proposer relationship: different
- Retrieval: rank 18, score 0.155, shared terms: based, chain, full, light, node, state
- Overlap evidence: Both projects address Cardano node functionality and state verification. Historical project focused on building a browser-based light node (Milestone 4), while current proposal focuses on stake-based threshold multi-sig for trustless state certification. The core technical goal of enabling lightweight state access is shared, but the specific mechanisms differ (browser extension vs. multi-sig certification).
- Funding evidence: Historical funding was 578,571.00 ADA; current proposal is 3,739,559.00 ADA.
- Relationship evidence: Different wallet addresses; Teragone Factory is a distinct entity from Harmonic Laboratories.
- Review notes: The historical project (Harmonic Laboratories) built a browser-based light node to follow the chain tip and update ledger state. The current proposal (Mithril Protocol) aims to solve similar infrastructure challenges (cost/complexity of verifying blockchain state) but proposes a different technical approach using stake-based threshold multi-sig rather than a browser extension. While the end goal of enabling efficient state verification is overlapping, the specific implementations are distinct enough to warrant medium confidence rather than high confidence.
- Source: https://treasury.sundae.fi/budgets/9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619/project/EC-0014-25

### MLabs - Cardano Tx Library: JavaScript/TypeScript Interface, Koios Backend, Hard Fork Maintenance

- Current proposer: MLabs LTD
- Current requested budget: 3,169,463.00 ADA
- Triage matches: 5

#### Project Catalyst: MLabs - CTL JavaScript / TypeScript Interface

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (no; 98,742.00 ADA)
- Proposer relationship: same
- Retrieval: rank 1, score 0.335, shared terms: building, chain, core, ctl, developers, development, interface, javascript, mlabs, off
- Overlap evidence: The current proposal explicitly states CTL has prior funding from Project Catalyst Funds 8, 9, 10, 11, and 13. The historical ID f14 corresponds to the specific work package of 'JavaScript/TypeScript Interface' described in the current proposal's WP1. The historical text mirrors the current text's goal of mapping CTL PS types/functions to JS/TS.
- Funding evidence: Historical status shows 'over_budget' and 'unfunded', but the work itself was previously proposed and funded under Project Catalyst, confirming the overlap is not new work.
- Relationship evidence: MLabs LTD is the current proposer; historical proposal was submitted by MLabs entities (p-lido-119971c0...), indicating a related or same organization.
- Review notes: The current proposal scopes out net new feature development (WP1, WP2) and forward-looking maintenance (WP3), claiming these are covered by the Intersect Open Source Committee. However, since WP1 (JS/TS Interface) was previously funded under Project Catalyst (F14), this proposal appears to be a continuation or re-funding of that specific work rather than entirely new scope. The overlap is high because the core functionality described in F14 is identical to WP1 in the current proposal.
- Source: https://www.catalystexplorer.com/en/proposals/mlabs-ctl-javascript-typescript-interface-f14

#### Project Catalyst: MLabs - CTL Blockfrost Backend

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 50,000.00 USD)
- Proposer relationship: different
- Retrieval: rank 2, score 0.234, shared terms: backend, been, blockfrost, building, ctl, developers, first, has, iog, layer
- Overlap evidence: Historical proposal funded Blockfrost backend integration; current proposal funds JavaScript/TypeScript interface, Koios backend (replacing or supplementing Blockfrost), and hard fork maintenance. Overlap is significant in the backend query layer scope but differs in language support and specific blockchain API targets.
- Funding evidence: Historical funding was $50,000 USD for Blockfrost backend; current budget is ~$3.17M ADA (~$1.4M USD) covering three work packages including JS/TS interface and Koios backend.
- Relationship evidence: Different legal entities (MLabs LTD vs p-lido-d825f00b-046e-4a79-b3fe-62865bf4ceb7) and distinct proposal titles indicating separate projects.
- Review notes: The historical proposal focused on adding Blockfrost as a query layer to CTL. The current proposal expands the scope to include JavaScript/TypeScript interfaces (a major new capability), adds Koios as a first-class option, and includes hard fork maintenance. While both address backend integration for Cardano developers, the specific APIs targeted differ (Blockfrost vs Koios) and the language support is significantly broader in the current proposal. The proposers are unrelated entities.
- Source: https://www.catalystexplorer.com/en/proposals/mlabs-ctl-blockfrost-backend-f9

#### Project Catalyst: MLabs: Advancing Plutarch and CTL: CIP Integration, API Enhancements, and Improved Infrastructure

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 487,679.00 ADA)
- Proposer relationship: different
- Retrieval: rank 8, score 0.186, shared terms: ctl, interface, mlabs, ogmios, support, supports, use
- Overlap evidence: Both proposals focus on upgrading the Cardano Tx Library (CTL). The historical proposal explicitly mentions upgrading CTL with NPM integration and an HTTP interface for Ogmios, which aligns with the current proposal's goal of adding a JavaScript/TypeScript interface and Koios backend. However, the current proposal is broader in scope, including hard fork maintenance and multiple query backends, whereas the historical proposal focused specifically on CIP integration and Ogmios HTTP switching.
- Funding evidence: The current proposal explicitly states that CTL has prior funding from Project Catalyst (IDs 8, 9, 10, 11, and 13), with ID f13 being the specific historical match. The current proposal is scoped to work not covered by the Intersect Open Source Committee, which historically funded core maintainership, suggesting a continuation of support for the same project but with different funding mechanisms.
- Relationship evidence: Historical proposer 'p-lido-d825f00b-046e-4a79-b3fe-62865bf4ceb7' is a distinct entity from current proposer 'MLabs LTD'. While both are MLabs-related entities, the historical proposal was submitted by a specific Lido-proposed grant recipient rather than MLabs Ltd directly.
- Review notes: The overlap is significant as both proposals address the modernization of CTL for JavaScript/TypeScript developers and adding Ogmios/Koios support. However, the confidence is medium because the proposers are not identical (one is a specific grant recipient entity, the other is MLabs Ltd), and the current proposal includes additional scope (hard fork prep, multiple backends) beyond the historical focus on CIPs and NPM integration.
- Source: https://www.catalystexplorer.com/en/proposals/mlabs-advancing-plutarch-and-ctl-cip-integration-api-enhancements-and-improved-infrastructure-f13

#### Project Catalyst: cardano-node typescript implementation

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: partial (no; 1,389,696.00 ADA)
- Proposer relationship: different
- Retrieval: rank 11, score 0.178, shared terms: developers, development, feature, not, protocol, that, typescript, use
- Overlap evidence: Both proposals address implementing a Cardano node in TypeScript to broaden developer access beyond PureScript/Unix users. Historical proposal focused on feature-complete implementation; current proposal focuses on the CTL library interface, Koios backend integration, and hard fork maintenance.
- Funding evidence: Current proposal budget is 3,169,463.00 ADA vs historical 1,389,696.00 ADA. Current proposal explicitly states it covers net new feature development (WP1, WP2) and forward-looking maintenance not covered by the Intersect Open Source Committee.
- Relationship evidence: Historical proposer IDs (p-lido-...) are distinct from current proposer (MLabs LTD); historical status is 'unfunded' and 'not_approved'.
- Review notes: While both proposals aim to bring Cardano node functionality to TypeScript developers, they target different artifacts (CTL library vs full node implementation) and have distinct proposers. The historical proposal was never funded, so there is no direct precedent of completed work overlap. The current proposal adds significant new scope (Koios backend, hard fork prep) beyond the historical text.
- Source: https://www.catalystexplorer.com/en/proposals/cardano-node-typescript-implementation-f10

#### Project Catalyst: MLabs - Cardano-Tx-Lib for web3

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: partial (yes; 71,000.00 USD)
- Proposer relationship: related
- Retrieval: rank 25, score 0.164, shared terms: building, developer, javascript, mlabs, support, transaction
- Overlap evidence: Both proposals address building a JavaScript/TypeScript interface for Cardano transactions (Cardano Tx Library). The historical proposal explicitly aimed to create an SDK for browser-based wallets and JS environments, while the current proposal focuses on opening CTL to JS/TS developers. However, the current proposal includes distinct new work packages (Koios backend integration and Dijkstra hard fork maintenance) not present in the historical scope.
- Funding evidence: Historical funding was $71,000 USD for web3.js-like SDK development; current budget is ~$3.17M ADA (~$1.4M USD equivalent) covering interface expansion, backend integration, and protocol maintenance.
- Relationship evidence: Proposer name 'MLabs LTD' matches historical recipient 'p-lido-d825f00b-046e-4a79-b3fe-62865bf4ceb7' (Lido's MLabs entity), indicating the same organization or direct successor.
- Review notes: The work represents a significant evolution of the same foundational library (Cardano Tx Library). The historical project laid the groundwork for JS transaction support, which is now being expanded into a full-fledged library with broader ecosystem adoption and protocol alignment. While the core mission overlaps heavily (JS transaction building), the current proposal adds substantial new scope (Koios backend, hard fork prep) that was not part of the original F8 proposal.
- Source: https://www.catalystexplorer.com/en/proposals/mlabs-cardano-tx-lib-for-web3-f8

### MLabs - Cardano.nix: 2026 Maintenance, Operator Tooling, and Dijkstra Readiness

- Current proposer: MLabs LTD
- Current requested budget: 1,144,433.00 ADA
- Triage matches: 3

#### Project Catalyst: MLabs – Streamlining Cardano Deployment with Enhanced NixOS Modules

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 217,140.00 ADA)
- Proposer relationship: same
- Retrieval: rank 1, score 0.223, shared terms: deployment, dev, mlabs, modules, nix, nixos, services, source, that, where
- Overlap evidence: Current proposal covers foundational maintenance and source build restoration (milestone 1), service module completion including Kupo/Ogmios (milestone 2), and Dijkstra readiness (milestone 6). Historical proposal focused on creating NixOS modules for Cardano services, which directly corresponds to the current work's core objective of establishing a declarative deployment path. The historical text mentions 'super modules' and simplifying complex interactions, while the current text details specific module completions and build path restoration.
- Funding evidence: Historical funding of 217,140.00 ADA covered initial development; current proposal of 1,144,433.00 ADA covers the 2026 cycle including maintenance, AI readiness, and Dijkstra preparation.
- Relationship evidence: MLabs LTD is the current proposer; historical proposal was submitted by p-lido-d825f00b-046e-4a79-b3fe-62865bf4ceb7 under Project Catalyst Fund 10, which MLabs explicitly states maintained since founding.
- Review notes: The work is highly overlapping as the current proposal represents a continuation and expansion of the foundational NixOS module work initiated in F10. The core task of building Nix modules for Cardano services was the primary goal of the historical proposal and remains central to the current one, with additional milestones adding AI integration and Dijkstra readiness.
- Source: https://www.catalystexplorer.com/en/proposals/mlabs-streamlining-cardano-deployment-with-enhanced-nixos-modules-f10

#### On-chain TreasuryWithdrawals: Withdraw ₳45,217 for MLabs Core Tool Maintenance & Enhancement: Cardano.nix

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 45,217.00 ADA)
- Proposer relationship: same
- Retrieval: rank 4, score 0.202, shared terms: across, audit, been, being, build, configuration, deployment, developer, developers, final
- Overlap evidence: Current proposal continues the exact same project (Cardano.nix maintenance) with expanded scope for 2026, building directly upon the foundational work funded in 2025. The core objective of maintaining the Nix flake suite for Cardano infrastructure is identical.
- Funding evidence: Historical funding of 45,217 ADA was used for annual maintenance and enhancements; current proposal requests 1,144,433 ADA for a full cycle including maintenance, tooling completion, and Dijkstra readiness, representing a continuation of the same work package.
- Relationship evidence: MLabs LTD is explicitly identified as the primary developer and maintainer of Cardano.nix in both texts; historical proposal submitted by Intersect on behalf of MLabs LTD.
- Review notes: The current proposal is a direct continuation of previously funded work by the same entity (MLabs LTD). The historical funding covered the foundational maintenance which the current proposal expands upon. There is no new independent work; the overlap is substantial as it represents the ongoing lifecycle of the same project.
- Source: ipfs://bafkreihj3ddbz7c52l2s3klalsf4ux5xqkawktom5v5apfral37hs6kpki

#### Treasury Fund 1: MLabs- Core Tool Maintenance: Cardano.nix & Plutarch, Research towards Tooling for Elliptical Curves

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 393,042.00 ADA)
- Proposer relationship: same
- Retrieval: rank 6, score 0.195, shared terms: audit, coverage, documentation, final, foundational, infrastructure, integration, maintenance, mlabs, nix
- Overlap evidence: Core work package of 'Cardano.nix' maintenance is identical between proposals. Historical proposal covered dependency updates, test suite validation, documentation, and hardfork compatibility checks for Cardano.nix. Current proposal continues this exact scope with added milestones for AI assistant readiness and Dijkstra readiness, which are extensions rather than new domains.
- Funding evidence: Historical funding of 393,042.00 ADA covered the foundational maintenance cycle; current proposal of 1,144,433.00 ADA represents a continuation and expansion of the same operational scope.
- Relationship evidence: Same legal entity (MLabs LTD) and identical wallet address; continuous maintenance relationship from Project Catalyst Fund 10 through Treasury Fund 1.
- Review notes: The proposal is a direct continuation of previously funded work by the same entity. The core deliverables (Cardano.nix maintenance, dependency updates, testing, documentation) are substantially reused. While new features (AI, Dijkstra) are added, they build upon the established foundation rather than representing distinct work domains.
- Source: https://treasury.sundae.fi/budgets/9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619/project/EC-0022-25,EC-0015-25,ER-0005-25

### MLabs - Covenant 2: Cross-Language Support and Developer Experience

- Current proposer: MLabsLTD
- Current requested budget: 1,461,441.00 ADA
- Triage matches: 8

#### Project Catalyst: MLabs: Path Analysis on Covenant

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (no; 99,861.00 ADA)
- Proposer relationship: same
- Retrieval: rank 1, score 0.236, shared terms: analysis, contract, covenant, developers, error, first, fully, languages, mlabs, path
- Overlap evidence: Current proposal describes Covenant as a compiler framework between high-level languages and Cardano bytecode. Historical proposal describes building a Haskell-based path analysis tool for Covenant to trace inputs/outputs for audits. The current proposal's core function (analysis, optimization, code generation) directly encompasses the historical work of path analysis, which is a critical component of static analysis.
- Funding evidence: Historical project was previously funded under Project Catalyst Fund 13 with 99,861.00 ADA but remains unfunded in the provided history (likely due to over-budget status). Current proposal budget is 1,461,441.00 ADA.
- Relationship evidence: Same MLabs team (MLabsLTD) responsible for both projects; historical project explicitly states it builds on the delivered Catalyst project.
- Review notes: The current proposal represents a natural evolution of the previously funded work. The historical project focused on path analysis for Covenant, while the current proposal expands Covenant's scope to include cross-language support and developer experience improvements. Since path analysis is a fundamental part of static analysis and code generation, the overlap is substantial (>=60%). The proposer is identical, confirming continuity of effort.
- Source: https://www.catalystexplorer.com/en/proposals/mlabs-path-analysis-on-covenant-f14

#### Project Catalyst: MLabs: Static analysis with Covenant

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 164,484.00 ADA)
- Proposer relationship: same
- Retrieval: rank 13, score 0.189, shared terms: analysis, contract, covenant, developers, languages, mlabs
- Overlap evidence: Current proposal describes Covenant as a compiler framework between high-level languages and bytecode, performing analysis, optimization, and code generation. Historical proposal defined Covenant as an eDSL with call-by-push semantics for static analysis and translation to UPLC. The current proposal's core function (analysis, optimization, code generation) is the direct evolution of the historical proposal's core function (static analysis, translation).
- Funding evidence: Historical funding was 164,484 ADA; current budget is 1,461,441 ADA. Historical status was 'approved' and project was 'feature complete'. Current proposal is the 'natural next step' extending functionality to cross-chain support.
- Relationship evidence: Same team (MLabsLTD) building upon a completed project; historical text explicitly states 'Covenant 1 was funded under Project Catalyst Fund 13 and is now feature complete' and 'delivered by the same MLabs team'.
- Review notes: The current proposal represents a significant expansion of previously funded work rather than new independent research. The core technology (Covenant) and its primary function (static analysis/code generation) were fully developed in the historical project. The new budget is primarily for DX improvements and cross-chain extension, which are natural continuations of the foundational work.
- Source: https://www.catalystexplorer.com/en/proposals/mlabs-static-analysis-with-covenant-f13

#### Project Catalyst: Cardano Smart Contract Generator | Generate and Deploy a Smart Contract in Under 1 Hour

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: partial (no; 200,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 18, score 0.179, shared terms: contract, developer, developers, experience, goal, smart, that, under
- Overlap evidence: The current proposal describes Covenant as a 'Cardano built compiler framework' that sits between high-level languages and bytecode, performing analysis, optimization, and code generation. The historical F13 proposal aimed to provide tools for 'smart contract creation' and 'automated auditing' via a web application. The text explicitly links the two by stating 'Covenant 1 was funded under Project Catalyst Fund 13 and is now feature complete,' identifying the current work as the 'natural next step.' The core functionality (compiler framework for smart contracts) is identical, with the current proposal expanding scope to cross-language support.
- Funding evidence: The historical proposal (F13) was previously funded under Project Catalyst Fund 13 with an amount of 200,000.00 ADA but has a status of 'unfunded' and 'over_budget', indicating the funding may have been insufficient or misallocated for the initial scope. The current proposal builds directly on this foundation.
- Relationship evidence: The current proposal explicitly states it is delivered by the same MLabs team that built Covenant 1, which was funded under Project Catalyst Fund 13. The historical source (F13) lists a proposer address associated with p-lido-89723b9c, while the current proposal is from MLabsLTD; however, the text confirms continuity of the project team and work lineage.
- Review notes: The overlap is high because the current proposal represents a direct continuation and stabilization/expansion of the work initiated in F13. While F13 was marked 'unfunded' and 'over_budget', the text confirms the team delivered Covenant 1 under that project, implying the core infrastructure exists. The current proposal's focus on improving developer experience and extending language support is an evolution of the original goal to enable faster smart contract innovation. The proposer relationship is confirmed by the explicit statement in the current text.
- Source: https://www.catalystexplorer.com/en/proposals/cardano-smart-contract-generator-generate-and-deploy-a-smart-contract-in-under-1-hour-f13

#### Project Catalyst: Bind to other Prog.Languages

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (no; 140,000.00 USD)
- Proposer relationship: same
- Retrieval: rank 19, score 0.177, shared terms: developer, developers, languages, more, other, that, their
- Overlap evidence: Current proposal explicitly states Covenant 1 was funded under Project Catalyst Fund 13 and is now feature complete. The current work extends the existing framework to support Solana bytecode, whereas the historical proposal focused on binding other Prog.Languages. The core technology (Covenant compiler) and goal (cross-language support) are identical.
- Funding evidence: Historical project was funded for $140,000 USD but remains unfunded/unapproved in this dataset context; current proposal builds directly on the delivered work of that historical project.
- Relationship evidence: Same team (MLabsLTD) building upon a completed project; historical proposer is a known entity associated with MLabs ecosystem.
- Review notes: The current proposal is a direct continuation and enhancement of previously funded work. The overlap is high because the foundational technology (Covenant) was already built and stabilized under the historical proposal. The new work adds specific cross-chain capabilities (Solana) rather than starting from scratch.
- Source: https://www.catalystexplorer.com/en/proposals/bind-to-other-proglanguages

#### On-chain TreasuryWithdrawals: IO: Developer Experience Initiative

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 3,601,926.00 ADA)
- Proposer relationship: different
- Retrieval: rank 2, score 0.223, shared terms: 2030, adoption, already, better, between, blockchain, both, builds, built, catalyst
- Overlap evidence: The current proposal focuses on extending the Covenant compiler framework to support cross-chain bytecode (Solana) and improving developer experience through documentation and error messages. The historical proposal ('IO: Developer Experience Initiative') funded a broader ecosystem-wide strategy including bounties, a 'cardano init' CLI, OpenZeppelin-style libraries, and portal unification. While both address developer experience barriers, the current proposal is a specific technical extension of an existing tool (Covenant 1) rather than a direct reuse of the historical funding's deliverables. The historical proposal was a general initiative with multiple components; the current proposal targets a specific compiler framework feature set.
- Funding evidence: The historical funding of 3,601,926 ADA covered a broad 'Developer Experience Initiative' including bounties and tooling unification. The current proposal of 1,461,441 ADA is for a specific technical milestone (Covenant 2) that builds on previously delivered work but does not appear to be the same project or a direct continuation of the historical funding's specific deliverables.
- Relationship evidence: None
- Review notes: The current proposal represents a natural technical evolution of Covenant 1, which was funded under Project Catalyst Fund 13. The historical proposal ('IO: Developer Experience Initiative') is a distinct, broader ecosystem initiative that aimed to unify tooling and documentation across the board via bounties and a CLI. While both aim to improve developer experience, they target different scopes: one is a specific compiler framework extension (Covenant), while the other was a general ecosystem strategy. There is no evidence of the same proposer or direct reuse of the historical proposal's funded work in the current proposal.
- Source: ipfs://QmUnSimkwuaXX357ugYxDkiUMzsKTYgcWvV74xWbiXUt3Y

#### Project Catalyst: Cardano Ecosystem : Smart Contract Languages LIve Support(Oxygen), Documentation and Adoption

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 96,900.00 ADA)
- Proposer relationship: different
- Retrieval: rank 11, score 0.192, shared terms: adoption, aiken, contract, developers, documentation, languages, plutarch, smart, support, these
- Overlap evidence: Current proposal builds directly on Covenant 1 (funded under F11) to extend cross-language support and improve DX; F11 focused on live support for languages including Aiken, Plutus, Plutarch, while current proposal focuses on compiler framework extension and multi-chain bytecode targeting.
- Funding evidence: Current budget 1,461,441.00 ADA vs historical 96,900.00 ADA; F11 was a small support grant, current is major infrastructure funding.
- Relationship evidence: Different legal entities (MLabsLTD vs p-lido-51dbb110-7b87-4c08-bc09-3aa8ec1837f4), though MLabs team built Covenant 1.
- Review notes: High confidence that Covenant 2 builds on F11 work, but low overlap in specific deliverables (F11=live support, C2=compiler framework extension). Proposers are distinct entities despite shared team lineage.
- Source: https://www.catalystexplorer.com/en/proposals/cardano-ecosystem-smart-contract-languages-live-supportoxygen-documentation-and-adoption-f11

#### On-chain TreasuryWithdrawals: IO & VacuumLabs: Enhancing Plutus - Performance, Correctness, and Usability

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 11,877,575.00 ADA)
- Proposer relationship: different
- Retrieval: rank 14, score 0.189, shared terms: 2030, adopted, adoption, already, analysis, becomes, better, between, beyond, blockchain
- Overlap evidence: Both proposals target the core compiler and developer experience layers of Cardano smart contracts. The historical proposal focused on enhancing Plutus (the native language) via formal verification, correctness guarantees, and compiler improvements for UPLC. The current proposal focuses on Covenant (a framework layer), extending it to cross-language support and improving DX. While the specific languages differ (Plutus vs. Aiken/Plutarch/Solana), the underlying work of optimizing compilation pipelines, reducing boilerplate, improving error messages, and establishing a robust compiler architecture is substantially overlapping. The current proposal explicitly states Covenant 1 was funded under Project Catalyst Fund 13, implying a lineage of tooling development that mirrors the historical funding.
- Funding evidence: Historical: ₳11,877,575 (IO & VacuumLabs). Current: ₳1,461,441 (MLabsLTD).
- Relationship evidence: None
- Review notes: The overlap is medium confidence because the specific deliverables differ (Plutus formalization vs. Covenant cross-language glue), but the strategic intent and technical domain (smart contract compilation efficiency and DX) are highly aligned. The historical proposal laid groundwork for compiler optimization and correctness, which the current proposal builds upon by creating a more universal framework. The proposers are unrelated entities.
- Source: ipfs://QmPkZ6Azo1tJfWVRjwn8G1Qk7k1SC3Vk3L21WFPSracCzg

#### Project Catalyst: Mesh New Features to Improve Developer experience and Cardano Adoption

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 200,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 20, score 0.173, shared terms: adoption, better, developer, developers, error, experience, messages, multiple, support
- Overlap evidence: Both proposals focus on improving developer experience through better error messages, tooling, and adoption. Covenant 2 extends this to cross-language support (Solana bytecode), while F12 focused on Mesh upgrades including CIP 45 and WebRTC. The core goal of enhancing DevXP is shared, but the specific technical implementations differ.
- Funding evidence: Covenant 1 was funded under Project Catalyst Fund 13 by MLabsLTD and is now feature complete. F12 was a separate proposal (ID: f12-mesh-new-features...) funded for 200,000 ADA by p-lido-fd267621-8783-4a03-99eb-a666496ea3d7. The current proposal builds on Covenant 1's completed work rather than reusing F12's specific Mesh features.
- Relationship evidence: Different legal entities (MLabsLTD vs p-lido-fd267621-8783-4a03-99eb-a666496ea3d7) and distinct project names (Covenant vs Mesh), though both operate within the Cardano ecosystem.
- Review notes: The current proposal is a distinct evolution of the Covenant framework, building upon previously funded work (Covenant 1) by the same team (MLabsLTD). While there is thematic overlap with the historical F12 proposal regarding developer experience improvements, the technical scope and proposer differ significantly. The overlap is moderate as both aim to improve tooling and adoption, but they address different specific tools (Covenant vs Mesh) and do not represent a direct reuse of the same codebase or substantial portion of work.
- Source: https://www.catalystexplorer.com/en/proposals/mesh-new-features-to-improve-developer-experience-and-cardano-adoption-f12

### MLabs - Grumplestiltskin 2: Pasta Curve Builtins and Kimchi PLookup Proof-of-Concept

- Current proposer: MLabs LTD
- Current requested budget: 1,144,433.00 ADA
- Triage matches: 7

#### On-chain TreasuryWithdrawals: Withdraw ₳104,347 for MLabs Research towards Tooling for Elliptical Curves...

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 104,347.00 ADA)
- Proposer relationship: same
- Retrieval: rank 1, score 0.202, shared terms: 381, across, all, any, applications, available, based, bls12, capabilities, chain
- Overlap evidence: Current proposal builds directly upon the parameterized curve framework delivered in Grumplestiltskin 1 (historical). Historical text specifies delivery of a 'parameterized elliptic curve and Galois field framework implemented in Plutarch' including 'Plutarch support for elliptic curve arithmetic'. Current proposal describes delivering 'UPLC builtins for the Pallas and Vesta curves, modeled on the existing CIP 381 BLS12 381 interface' and states 'This continues from the original Grumplestilskin project... Where Grumplestilskin 1 made any curve usable in Plutarch... Grumplestiltskin 2 adds specific high value curves at the protocol level'.
- Funding evidence: Historical funding of 104,347.00 ADA for 'GrumpleStiltSkin' which delivered the open source parameterized framework; current proposal budget is 1,144,433.00 ADA for implementing specific curve builtins and a Kimchi PLookup PoC that extends the foundational work.
- Relationship evidence: Same proposer (MLabs LTD); Historical text explicitly references 'GrumpleStiltSkin' as the project being funded, while current proposal describes 'Grumplestiltskin 2' as continuing from the original project.
- Review notes: The current proposal represents a direct evolution of previously funded work rather than independent research. The historical funding successfully delivered the core parameterized framework (Grumplestiltskin 1), enabling the use of arbitrary curves in Plutarch. The current proposal (Grumplestiltskin 2) focuses on extending this by adding specific high-value curves as protocol-level builtins and implementing a new proof system (Kimchi PLookup). The overlap is substantial because the current work cannot exist without the foundational framework delivered previously, and the proposer remains the same entity.
- Source: ipfs://bafkreig4bosl5dfpmtqguybf4yaffkwo5hcaxxy2k7wlbwdl57twojfk2i

#### Treasury Fund 1: MLabs- Core Tool Maintenance: Cardano.nix & Plutarch, Research towards Tooling for Elliptical Curves

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 393,042.00 ADA)
- Proposer relationship: same
- Retrieval: rank 5, score 0.161, shared terms: 381, all, any, available, bls12, cannot, core, curve, curves, elliptic
- Overlap evidence: Current proposal builds directly on the parameterized curve framework delivered in Grumplestiltskin 1 (historical work). Historical funding covered core tooling maintenance for Plutarch and research into elliptic curve operations, which are the exact prerequisites for the current proposal's implementation of Pasta curves and Kimchi PLookup proofs.
- Funding evidence: Historical funding ($393,042.00) was contracted for tool maintenance and research; current budget ($1,144,433.00) is significantly larger, indicating a progression from foundational tooling to specific high-value curve implementation rather than redundant work.
- Relationship evidence: Same legal entity (MLabs LTD) and identical project team context; historical text explicitly references 'The Grumplestiltskin project' as the predecessor.
- Review notes: The proposal represents a logical evolution of previously funded work (Grumplestiltskin 1) by the same entity. The historical funding established the necessary Plutarch tooling and curve research framework, which the current proposal now implements at the protocol level via CIPs. This is not redundant but rather an additive step in the project lifecycle.
- Source: https://treasury.sundae.fi/budgets/9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619/project/EC-0022-25,EC-0015-25,ER-0005-25

#### Project Catalyst: Empowering Developers with Midnight and Zero-Knowledge Proofs (ZKPs) for Enhanced Privacy and Security in DApps

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 100,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 6, score 0.160, shared terms: applications, gap, knowledge, many, privacy, proofs, using, zero, zkps
- Overlap evidence: Both proposals address Zero Knowledge Proofs (ZKPs) on Cardano, but the historical proposal focused on developer education regarding Midnight/ZKPs, while the current proposal focuses on technical implementation of Pasta Curve builtins and Kimchi PLookup. The overlap is in the general domain of ZKP infrastructure rather than specific work.
- Funding evidence: Historical project was not funded (status: unfunded/not_approved). Current project builds upon Grumplestiltskin 1 (2025 proposal) and MLabs Catalyst Fund 12, not the historical source.
- Relationship evidence: Different legal entities (MLabs LTD vs p-lido-b9529eac-7b49-4629-9ad2-6f9ec408b150) and distinct project scopes.
- Review notes: The current proposal represents a significant technical evolution from the historical proposal. While both deal with ZKPs, the historical work was educational and focused on Midnight, whereas the current work is implementation-focused on Pasta curves and Kimchi PLookup. The proposers are unrelated entities, and the historical project did not receive funding.
- Source: https://www.catalystexplorer.com/en/proposals/empowering-developers-with-midnight-and-zero-knowledge-proofs-zkps-for-enhanced-privacy-and-security-in-dapps-f13

#### Project Catalyst: MLabs - Purus: PureScript to Plutus Core compiler

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 619,761.00 ADA)
- Proposer relationship: same
- Retrieval: rank 7, score 0.158, shared terms: all, chain, core, has, level, mlabs, performance, plutarch, plutus, some
- Overlap evidence: Current proposal relies on the UPLC framework and curve operations developed in Grumplestiltskin 1 (referenced as complementary), which was built upon the compiler infrastructure from the historical Purus project. The current proposal explicitly states it continues from Grumplestiltskin 1, while the historical text describes creating the PureScript to Plutus Core compiler backend for UPLC, which is the foundational layer enabling the curve operations in the current proposal.
- Funding evidence: Historical funding of 619,761.00 ADA approved; current budget is 1,144,433.00 ADA.
- Relationship evidence: Same legal entity (MLabs LTD) and technical ecosystem; historical proposer is a known MLabs project identifier.
- Review notes: The current proposal represents an evolution of work initiated by the same proposer. The historical project (Purus) established the compiler backend for UPLC, which is a prerequisite for the curve builtins and Kimchi PLookup implementation proposed here. While not identical, the core technical infrastructure (UPLC compilation pipeline) is directly reused, constituting significant overlap rather than adjacent work.
- Source: https://www.catalystexplorer.com/en/proposals/mlabs-purus-purescript-to-plutus-core-compiler-f10

#### Project Catalyst: MLabs: Advancing Plutarch and CTL: CIP Integration, API Enhancements, and Improved Infrastructure

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 487,679.00 ADA)
- Proposer relationship: same
- Retrieval: rank 12, score 0.151, shared terms: better, cases, cip, interface, mlabs, performance, plutarch, support, use, via
- Overlap evidence: Current proposal builds directly upon Grumplestiltskin 1 (referenced in text), which was funded by the historical proposal to establish the parameterized curve framework in Plutarch. The current work extends this foundation by adding specific high-value curves and Kimchi PLookup, whereas the historical work focused on general CIP integration and API enhancements.
- Funding evidence: Historical funding of 487,679.00 ADA supported the core infrastructure (Plutarch/CTL) that the current proposal relies upon; current budget is 1,144,433.00 ADA for specific curve implementation and proof-of-concept verification.
- Relationship evidence: Same legal entity (MLabs LTD) and technical team; historical proposal explicitly references the current project as a continuation.
- Review notes: The proposals represent a sequential development relationship rather than redundant work. The historical funding established the necessary tooling (Plutarch) which the current proposal leverages to implement specific advanced features (Pasta curves, Kimchi). While there is significant overlap in the underlying technology stack and team, the scope has expanded from general infrastructure to specialized curve implementation.
- Source: https://www.catalystexplorer.com/en/proposals/mlabs-advancing-plutarch-and-ctl-cip-integration-api-enhancements-and-improved-infrastructure-f13

#### Project Catalyst: Incorporating Plonk into AK-381 Zero-Knowledge Library

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 100,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 13, score 0.149, shared terms: 381, applications, high, knowledge, library, zero
- Overlap evidence: Both proposals address ZKP libraries on Cardano. Current proposal builds upon Grumplestiltskin 1 (2025) which used a parameterized curve framework in Plutarch, whereas historical work focused on integrating PLONK into AK-381. Current proposal adds Pasta curves and Kimchi PLookup via UPLC builtins; historical work was limited to PLONK integration without the specific curve family or recursive composition capabilities.
- Funding evidence: Historical funding was 100,000 ADA (unfunded). Current budget is 1,144,433.00 ADA. Historical project status 'over_budget' suggests scope expansion beyond original goals, but the core work did not reach completion.
- Relationship evidence: Historical proposer names (p-lido-*) are distinct from current proposer (MLabs LTD). Historical status is 'unfunded' and 'over_budget', indicating the project did not proceed to completion.
- Review notes: The current proposal represents a significant evolution from the historical work, moving from PLONK integration to Pasta curve support and Kimchi PLookup. While there is conceptual overlap in ZKP library development, the specific technical implementations (Pasta curves vs PLONK) and proposer identities differ substantially. The historical project was not funded and did not complete its scope.
- Source: https://www.catalystexplorer.com/en/proposals/incorporating-plonk-into-ak-381-zero-knowledge-library-f12

#### Project Catalyst: Zero-Knowledge Proofs (ZKP) SDK for Privacy in Cardano

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 200,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 20, score 0.145, shared terms: data, knowledge, preserving, privacy, proofs, without, zero, zkp
- Overlap evidence: Both proposals address Zero Knowledge Proofs (ZKP) on Cardano. The historical proposal sought a general ZKP SDK for privacy applications. The current proposal focuses specifically on implementing Pasta Curve builtins and Kimchi PLookup proofs, building upon the parameterized curve framework from Grumplestiltskin 1 (2025). The overlap is significant in domain (ZKP infrastructure) but distinct in specific technical implementation (Pasta vs BLS12-381), representing a complementary rather than redundant effort.
- Funding evidence: Historical proposal was unfunded and over budget. Current proposal budget is 1,144,433.00 ADA. Historical funding status does not indicate prior completion of the current work's specific goals.
- Relationship evidence: Historical proposer names (p-lido-...) are distinct from current proposer (MLabs LTD). While MLabs delivered the YTxP framework used in the historical text, the historical proposal was funded by p-lido entities and is marked as unfunded.
- Review notes: The proposals share a common thematic focus on ZKP infrastructure but target different technical curves (Pasta vs BLS12-381) and implementation stages (SDK framework vs Plutus Core builtins). The historical proposal was not funded, so it does not represent completed work covering the current proposal. The proposer relationship is weak; while MLabs contributed to the YTxP framework mentioned in the text, they are not the same entity as the historical p-lido proposers.
- Source: https://www.catalystexplorer.com/en/proposals/zero-knowledge-proofs-zkp-sdk-for-privacy-in-cardano-f13

### MLabs - TrueInventory: An accessible blockchain inventory for videogame developers

- Current proposer: MLabs LTD
- Current requested budget: 2,850,783.00 ADA
- Triage matches: 7

#### Project Catalyst: MLabs – Cardano Game Engine Wallet - Godot Integration

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 547,380.00 ADA)
- Proposer relationship: same
- Retrieval: rank 1, score 0.240, shared terms: blockchain, current, developers, engine, engines, game, games, godot, integration, mlabs
- Overlap evidence: The current proposal builds upon the historical F10 project by extending the core concept of integrating blockchain wallet functionality into the Godot game engine. While F10 focused on 'light wallet functionality' for quick integration, TrueInventory expands this to a complete inventory management service with tokenization, crafting, and transfer features, utilizing the same foundational work of embedding Cardano cryptographic tooling within Godot.
- Funding evidence: Historical funding was 547,380.00 ADA; current budget is 2,850,783.00 ADA. The historical project established the technical feasibility and codebase for engine integration, which the current proposal leverages to deliver a more comprehensive ecosystem solution.
- Relationship evidence: Current proposer MLabs LTD explicitly cites prior Catalyst funded Godot wallet integration work and a Mina Foundation funded Godot wallet integration as direct experience at the intersection of Cardano tooling and game engine code.
- Review notes: The current proposal represents a significant evolution of previously funded work rather than independent research. The core technical challenge addressed in F10 (integrating Cardano into Godot) is the same as in TrueInventory, with the latter adding substantial features on top of that foundation. This constitutes high confidence overlap as the proposer is explicitly building on prior funded experience.
- Source: https://www.catalystexplorer.com/en/proposals/mlabs-cardano-game-engine-wallet-godot-integration-f10

#### Project Catalyst: Standardizing Seamless Blockchain Integration for Unity Game Engine

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 690,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 2, score 0.232, shared terms: blockchain, developers, engine, experience, game, get, integration, that, unity
- Overlap evidence: Both proposals address blockchain integration for game engines (Unity/Godot) on Cardano, focusing on SDK/API development. Current proposal builds on prior Catalyst and Mina Foundation funded Godot wallet integration work, indicating a shared technical domain of game engine interoperability.
- Funding evidence: Previous proposal was not approved; current proposal budget is significantly higher (2.85M vs 0.69M).
- Relationship evidence: Different proposers (MLabs LTD vs p-lido-4b24b2d3-3212-4b87-94b1-99de8b23b3ab); no direct organizational link indicated.
- Review notes: The proposals share significant thematic overlap in solving blockchain integration for game engines, but the proposers are unrelated and the previous work was not funded. The current proposal explicitly references prior experience with Godot wallet integration, suggesting continuity in technical approach rather than direct reuse of specific deliverables.
- Source: https://www.catalystexplorer.com/en/proposals/standardizing-seamless-blockchain-integration-for-unity-game-engine-f10

#### Project Catalyst: Cardano Game Development SDK for Godot

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: partial (no; 84,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 3, score 0.213, shared terms: apis, developers, engine, game, games, godot, integration, source
- Overlap evidence: Both proposals address Cardano integration with the Godot game engine. Historical proposal focused on SDK/APIs/WebGL templates for developers; current proposal builds a complete inventory management service with audited smart contracts and client libraries, representing an evolution of the same technical domain.
- Funding evidence: Historical proposal was unfunded but over budget; current proposal is significantly larger (2.85M ADA vs 84K ADA) and aims for broader ecosystem adoption rather than just SDK development.
- Relationship evidence: Different proposers (MLabs LTD vs p-lido-806e474f-3a31-4653-9a1c-6e71485f0216); MLabs explicitly cites prior work as inspiration rather than claiming ownership.
- Review notes: The current proposal represents a substantial expansion of the foundational work proposed historically, moving from basic SDK integration to a full-featured inventory system. While the proposers are unrelated, the technical scope overlaps significantly in the Godot/Cardano intersection, warranting medium confidence.
- Source: https://www.catalystexplorer.com/en/proposals/cardano-game-development-sdk-for-godot-f12

#### Project Catalyst: Unreal Engine Plugin for Cardano Blockchain Interactions

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 200,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 4, score 0.211, shared terms: blockchain, developers, engine, game, games, source, unreal
- Overlap evidence: Both proposals target Unreal Engine integration with Cardano blockchain functionality. The current proposal builds on prior Catalyst funded Godot wallet integration work and a Mina Foundation funded Godot wallet integration, indicating a broader strategy of engine integration rather than direct reuse of the specific Unreal plugin work.
- Funding evidence: Historical project was not approved and received no funding; current proposal budget is significantly higher.
- Relationship evidence: No evidence of same or related proposer; historical proposer names are distinct from MLabs LTD.
- Review notes: The proposals share thematic overlap in targeting game engines for Cardano integration, but the historical project was specifically for Unreal Engine while the current proposal focuses on a general inventory system supporting multiple engines (Godot, Unity, Unreal). The lack of proposer similarity and the historical project's unfunded status suggest limited direct reuse, though both aim to improve developer tooling for blockchain games.
- Source: https://www.catalystexplorer.com/en/proposals/unreal-engine-plugin-for-cardano-blockchain-interactions-f13

#### Project Catalyst: Anvil - Open Source - Universal Wallet Connector (Weld) for Unity, Godot, and Game Maker

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 90,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 6, score 0.201, shared terms: blockchain, developers, engines, game, godot, limited, source, there, unity, wallet
- Overlap evidence: Both proposals address wallet connectivity for game engines (Unity, Godot). The historical project focused on a 'Universal Wallet Connector' (Weld), while the current proposal builds upon this by creating a complete inventory management service with tokenization. The current text explicitly states it builds on prior Catalyst funded Godot wallet integration work.
- Funding evidence: Historical funding was 90,000 ADA; current budget is 2,850,783.00 ADA.
- Relationship evidence: None identified. Historical proposer addresses are p-lido-* variants, while current proposer is MLabs LTD.
- Review notes: The current proposal represents a significant evolution of the historical work rather than direct reuse. While both aim to improve Cardano integration for game developers using similar engines (Unity/Godot), the scope has expanded from a wallet connector to a full inventory management system with tokenization and multi-engine support. The proposers are unrelated entities, indicating independent development building on prior community knowledge.
- Source: https://www.catalystexplorer.com/en/proposals/anvil-open-source-universal-wallet-connector-weld-for-unity-godot-and-game-maker-f13

#### Project Catalyst: WALLET ADD-ONS FOR GAME ENGINE

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 26,825.00 USD)
- Proposer relationship: different
- Retrieval: rank 8, score 0.184, shared terms: client, engine, game, source, that, there, wallet
- Overlap evidence: Both proposals address wallet add-ons for game engines (specifically Godot) on Cardano. The current proposal builds upon prior Catalyst funded work for Godot wallet integration and a Mina Foundation funded project, indicating the core technical challenge of integrating blockchain wallets into game engine clients is being revisited with an expanded scope to include inventory management and tokenization rather than just wallet functionality.
- Funding evidence: The historical proposal was not approved and received no funding. The current proposal has a significantly higher budget ($2,850,783 vs $26,825) and represents a foundational ecosystem project rather than a specific studio add-on.
- Relationship evidence: None identified; proposers are distinct entities.
- Review notes: While the technical domain (game engine wallet integration) overlaps significantly with the historical proposal, the current work expands the scope to full inventory management and tokenization. The lack of prior funding for the historical proposal suggests it was not a realized project, making the current proposal's claim of building on 'direct, recent experience' more about conceptual lineage than direct code reuse. The proposers are unrelated.
- Source: https://www.catalystexplorer.com/en/proposals/wallet-add-ons-for-game-engine-f9

#### Project Catalyst: NMKR SDK for Godot

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 80,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 22, score 0.169, shared terms: access, developers, engine, game, godot, minting, more, that, there, while
- Overlap evidence: Current proposal builds directly on the Godot wallet integration work from the historical proposal, extending it to full inventory management and tokenization rather than just minting. The core technical challenge of integrating Cardano cryptographic tooling with the Godot engine is identical.
- Funding evidence: Historical funding was 80,000 ADA for SDK/minting; current budget is 2,850,783.00 ADA for a complete ecosystem service including server APIs and multi-engine support.
- Relationship evidence: Different legal entities (MLabs LTD vs p-lido-adf1e9b0-4503-484d-be7e-fd21f5b7bb68); no shared proposer identifiers.
- Review notes: The current proposal represents a substantial evolution of the previously funded work, moving from a specific minting SDK to a comprehensive inventory management system. While the proposer is different, the technical foundation and engineering challenges are directly derived from the prior project.
- Source: https://www.catalystexplorer.com/en/proposals/nmkr-sdk-for-godot-f12

### MLabs Core Tool Maintenance & Enhancement: Plutarch and Ply

- Current proposer: MLabs LTD
- Current requested budget: 1,144,433.00 ADA
- Triage matches: 4

#### On-chain TreasuryWithdrawals: Withdraw ₳243,478 for MLabs Core Tool Maintenance & Enhancement: Plutarch

- Match confidence: high
- Estimated current-work overlap: 95%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 243,478.00 ADA)
- Proposer relationship: different
- Retrieval: rank 1, score 0.336, shared terms: annual, audit, been, blog, both, budget, bug, chain, compatibility, contract
- Overlap evidence: Both proposals fund identical core work (Plutarch maintenance/enhancement). Historical proposal covers annual maintenance, bug fixes, hardfork compatibility, and feature implementation. Current proposal covers exactly these same priorities plus Ply tooling, which is a natural extension of the existing Plutarch ecosystem.
- Funding evidence: Historical funding was ₳243,478 for Plutarch maintenance; current funding is ₳1,144,433 covering both Plutarch and Ply. The scope has expanded but the foundational work remains identical.
- Relationship evidence: Historical text explicitly states: 'MLabs LTD is the primary developer and maintainer' and that funding was submitted 'by Intersect on behalf of the vendor'.
- Review notes: The proposal represents a continuation of previously funded work by the same underlying entity (MLabs LTD), though administered through different proposers (Intersect vs MLabs LTD). The work overlap is high as it addresses the exact same maintenance and compatibility needs for Plutarch, with only a minor addition of Ply. This is not new work but an expansion of existing funded obligations.
- Source: ipfs://bafkreienjc55atyjxfy7ij2mthoud6m2um5snifhjvurflfujf4s2sa3le

#### Treasury Fund 1: MLabs- Core Tool Maintenance: Cardano.nix & Plutarch, Research towards Tooling for Elliptical Curves

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 393,042.00 ADA)
- Proposer relationship: same
- Retrieval: rank 4, score 0.251, shared terms: audit, bug, building, cannot, changes, compatibility, contract, core, documentation, enhancement
- Overlap evidence: Current proposal explicitly seeks annual funding for 'maintenance and enhancement of Plutarch', which is the exact scope of the historical proposal ('continuous support including maintenance releases, bug fixes, and compatibility updates for Plutarch'). The historical text details identical deliverables (quarterly dependency updates, hardfork compatibility checks, documentation) for Plutarch. The current proposal adds Ply but retains the core Plutarch maintenance work as a primary component.
- Funding evidence: Historical funding of 393,042 ADA covered 12 months of Plutarch maintenance; current budget of 1,144,433 ADA covers an annual period including both Plutarch and Ply. The historical proposal was 'contracted' (funded) before being paused.
- Relationship evidence: Same legal entity (MLabs LTD) and identical funding structure (quarterly milestones for Plutarch dependency updates and hardfork compatibility).
- Review notes: The current proposal represents a direct continuation of the previously funded work on Plutarch maintenance by the same entity. The addition of Ply is an expansion, but the core obligation to maintain Plutarch is identical to the historical contract. Given the explicit reuse of the same tooling and funding model, this constitutes high-confidence overlap.
- Source: https://treasury.sundae.fi/budgets/9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619/project/EC-0022-25,EC-0015-25,ER-0005-25

#### Project Catalyst: MLabs: Tooling upgrade for Conway compatibility.

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: significant_partial
- Previously proposed: True
- Previously funded relevance: none (yes; 197,850.00 ADA)
- Proposer relationship: different
- Retrieval: rank 5, score 0.232, shared terms: compatibility, core, era, maintenance, mlabs, tooling
- Overlap evidence: Both proposals address the maintenance and Conway-era compatibility of MLabs core tooling (Plutarch/Ply), but the current proposal is broader, covering ongoing evolution beyond just Conway compatibility.
- Funding evidence: The historical funding of 197,850.00 ADA covered specific Conway upgrades, while the current budget of 1,144,433.00 ADA covers a wider scope including protocol era compatibility and general maintenance.
- Relationship evidence: Proposers are distinct entities (MLabs LTD vs p-lido-d825f00b-046e-4a79-b3fe-62865bf4ceb7) with no shared domain similarity indicating a related organization.
- Review notes: While the work is related (same tooling, similar goals), the proposer is different, suggesting this is not a reuse case but rather a continuation or expansion of work by a new entity. The overlap is significant in terms of subject matter but does not meet the threshold for high confidence due to the lack of proposer relationship.
- Source: https://www.catalystexplorer.com/en/proposals/mlabs-tooling-upgrade-for-conway-compatibility-f13

#### Project Catalyst: MLabs - Plutarch v2

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: partial (yes; 73,040.00 USD)
- Proposer relationship: different
- Retrieval: rank 13, score 0.201, shared terms: chain, developer, edsl, fully, mlabs, off, plutarch
- Overlap evidence: Both proposals focus on the maintenance and enhancement of Plutarch, a Haskell eDSL for Cardano smart contracts. The historical proposal aimed to expand Plutarch's feature set and efficiency, while the current proposal focuses on ongoing maintenance, protocol era compatibility (e.g., Dijkstra), and vulnerability fixes. The core subject matter (Plutarch tooling) is identical, but the scope has evolved from initial expansion to long-term ecosystem support.
- Funding evidence: The historical funding was $73,040 USD for Plutarch v2 expansion. The current funding is $1,144,433 ADA (approx. $580k+ USD at current rates) for annual maintenance and enhancement. This represents a significant increase in scale and duration, indicating that the previous work was foundational but does not fully cover the current comprehensive maintenance scope.
- Relationship evidence: The historical text explicitly mentions 'p-lido-d825f00b-046e-4a79-b3fe-62865bf4ceb7' as the recipient, whereas the current proposal is attributed to 'MLabs LTD'. There is no textual evidence linking these two specific entities as the same legal entity or directly related parties in this context.
- Review notes: The proposal involves substantial reuse of the Plutarch tooling described in the historical record. However, the proposers are distinct entities (historical recipient vs. current proposer), preventing a high-confidence match. The overlap is significant because both proposals address the same core technology (Plutarch) and its role in the Cardano ecosystem, but the current proposal represents a broader, ongoing maintenance effort rather than the initial development phase covered historically.
- Source: https://www.catalystexplorer.com/en/proposals/mlabs-plutarch-v2-f9

### MLabs: Better arrays for everyone

- Current proposer: MLabs LTD
- Current requested budget: 1,378,470.00 ADA
- Triage matches: 1

#### Treasury Fund 1: Input Output Engineering Core Development Proposal (5of6)

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 11,492,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 6, score 0.195, shared terms: aiken, array, arrays, art, cip, contract, core, data, develop, developer
- Overlap evidence: The current proposal explicitly aims to bring Plinth and Aiken up to parity with Plutarch for CIP 138 array support, which directly addresses MS14.3 (CIP 0138: builtin arrays) from the historical proposal. It also plans to propose a new CIP for array primitives in Plutus Core, covering MS14.10 (Plinth compiler enhancement), MS14.12 (performance benchmarking), and MS14.13 (compiler certifier). The historical proposal's goal of enhancing Plinth and Aiken is the primary driver of the current work.
- Funding evidence: The historical funding of 11,492,000.00 ADA covered the foundational CIPs including arrays (MS14.3) and compiler enhancements (MS14.10), which form the basis of the current proposal's scope.
- Relationship evidence: Input Output Engineering (IOG) is a distinct entity from MLabs LTD; IOG was the original developer of Plutus Core and CIPs, while MLabs is an independent organization.
- Review notes: While the work is highly overlapping with previously funded IOG proposals, the proposers are different entities. The historical funding was substantial and covered the core technical roadmap items that this new proposal intends to execute or expand upon. The overlap is not merely textual but represents a direct continuation of specific CIPs (especially CIP 138 arrays) originally scoped in the historical document.
- Source: https://treasury.sundae.fi/budgets/9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619/project/UTXO-EC-0002-25-05

### MLabs: Encrypted Programmable Tokens with TFHE

- Current proposer: MLabs LTD
- Current requested budget: 1,343,564.00 ADA
- Triage matches: none.

### MLabs: Open-Sourcing FeesaSwap as Live Fee Abstraction Infrastructure on Cardano

- Current proposer: MLabs LTD
- Current requested budget: 686,660.00 ADA
- Triage matches: 4

#### Project Catalyst: MLabs FeesaSwap: Wallet & dApp Ready ADA-less Tx Fees

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (no; 194,914.00 ADA)
- Proposer relationship: same
- Retrieval: rank 2, score 0.268, shared terms: backend, conversions, dapps, fees, feesaswap, friction, kyc, less, live, lost
- Overlap evidence: Both texts describe FeesaSwap as live infrastructure enabling ADA-less transactions, removing the need for users to acquire ADA first. The current proposal explicitly states it will 'open source' and 'harden' the protocol, while the historical text confirms the backend was scaled and oracles added for wallet/dApp integration. The core value proposition and technical implementation are identical.
- Funding evidence: Historical funding of 194,914.00 ADA covered the prototype and launch phase; current proposal budget of 686,660.00 ADA is for open-sourcing and hardening existing IP, representing a continuation rather than new development.
- Relationship evidence: Proposer name 'MLabs LTD' matches historical recipient names 'p-lido-119971c0...' and 'p-lido-6a6124a2...' which are known MLabs project identifiers; both proposals address the exact same problem (ADA-less fees) using the identical solution (FeesaSwap).
- Review notes: The current proposal is a direct expansion of previously funded work by the same entity. The historical project successfully built and launched FeesaSwap; this proposal focuses on making that infrastructure open source and more robust. There is no meaningful new work being proposed beyond what was already funded, as the core product and its purpose are identical.
- Source: https://www.catalystexplorer.com/en/proposals/mlabs-feesaswap-wallet-dapp-ready-ada-less-tx-fees-f15

#### On-chain TreasuryWithdrawals: IO: Cardano Upgrades

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 13,103,039.00 ADA)
- Proposer relationship: different
- Retrieval: rank 21, score 0.173, shared terms: 2030, abstraction, acquire, active, adoption, annual, applications, asset, available, barrier
- Overlap evidence: The current proposal (FeesaSwap) and the historical proposal (IO: Cardano Upgrades) address identical technical problems: removing the requirement for users to hold ADA to pay transaction fees. The historical proposal explicitly includes 'Babel Fees' as a workstream that allows fee payment in any native asset, which is functionally equivalent to the current FeesaSwap infrastructure. The current proposal aims to open-source this functionality, while the historical proposal funded the design and implementation of the underlying ledger primitives (CIP 159) and application layer logic (Babel Fees). The overlap is substantial because the core value proposition and technical solution are identical.
- Funding evidence: The historical proposal was funded with 13,103,039.00 ADA to deliver three coordinated initiatives including Babel Fees, which enables fee payment in non-ADA assets. The current proposal seeks 686,660.00 ADA specifically for open-sourcing and hardening the FeesaSwap IP that was developed under the historical funding.
- Relationship evidence: None
- Review notes: The current proposal represents a downstream implementation of work previously funded under the 'IO: Cardano Upgrades' initiative. The core functionality (paying fees in non-ADA tokens) is explicitly described in the historical text as 'Babel Fees'. While the proposers are different, the technical work is not additive but rather an open-sourcing and stabilization effort for infrastructure already built and funded.
- Source: ipfs://QmeNzwKE9bMyr65E4Dxtvoji7WBbazXUVykqQWq1pHXZvQ

#### Project Catalyst: MLabs - Feesaswap: Decentralized Fee Trading on Cardano

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 415,529.00 ADA)
- Proposer relationship: different
- Retrieval: rank 1, score 0.332, shared terms: conversions, dapps, exchange, fee, fees, feesaswap, infrastructure, mlabs, most, production
- Overlap evidence: Both proposals address the same core problem (Cardano ADA fee requirements) and solution concept (decentralized fee trading/abstraction), but the historical proposal was unfunded and focused on 'trading' while the current proposal focuses on 'open-sourcing infrastructure' for wallets/dApps.
- Funding evidence: Historical proposal was previously funded with 415,529.00 ADA but marked as 'over_budget' and 'unfunded', indicating the work did not proceed to completion or adoption.
- Relationship evidence: Historical proposer 'p-lido-991a644e-2f67-4dc9-92d7-4a49b4fe2b4c' is a distinct entity from current proposer 'MLabs LTD'.
- Review notes: The current proposal represents a significant evolution of the historical concept (FeesaSwap) from a trading mechanism to open-source infrastructure. While the core utility is identical, the shift in focus and the lack of continuity in funding suggest this is a new iteration rather than direct reuse of prior funded work.
- Source: https://www.catalystexplorer.com/en/proposals/mlabs-feesaswap-decentralized-fee-trading-on-cardano-f14

#### Project Catalyst: MLabs: Pisa-Fees: Enabling Decentralized Fee Trading on Cardano

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 499,693.00 ADA)
- Proposer relationship: different
- Retrieval: rank 3, score 0.246, shared terms: conversions, exchange, fee, fees, mlabs, product, token, tokens
- Overlap evidence: Both proposals address decentralized fee trading on Cardano without ADA conversion; current proposal explicitly references open-sourcing FeesaSwap as live infrastructure, while historical proposal focused on enabling the mechanism via Pisa Fees.
- Funding evidence: Historical funding of 499,693.00 ADA approved for similar functionality; current proposal budget is 686,660.00 ADA.
- Relationship evidence: Different legal entities (MLabs LTD vs p-lido-d825f00b-046e-4a79-b3fe-62865bf4ceb7); low proposer similarity score (0.125).
- Review notes: The core technical objective (fee abstraction without ADA conversion) is substantially reused between the two proposals. However, the proposers are distinct entities with no clear relationship evidence, and the historical project was completed under a different entity (Pisa Fees vs FeesaSwap). The overlap is significant but not identical, warranting medium confidence.
- Source: https://www.catalystexplorer.com/en/proposals/mlabs-pisa-fees-enabling-decentralized-fee-trading-on-cardano-f13

### MLabs: Post-quantum signature verification support

- Current proposer: MLabs LTD
- Current requested budget: 4,005,516.00 ADA
- Triage matches: none.

### Nula: Cardano's token streaming protocol

- Current proposer: Five Binaries
- Current requested budget: 952,750.00 ADA
- Triage matches: 1

#### Project Catalyst: C Streaming Protocol: Real-Time Continuous Payment Standard

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 68,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 3, score 0.223, shared terms: dao, flows, native, payroll, protocol, standard, streaming, time, treasury
- Overlap evidence: Both proposals address the exact same technical gap: a native Cardano token streaming protocol for real-time continuous payments. The current proposal explicitly cites Superfluid and Sablier as proven primitives on other chains, mirroring the historical proposal's claim that Cardano lacks such a standard. Core functionality (locking tokens at fixed accrual rates, flexible withdrawal options, zero platform fees) is identical in intent and design.
- Funding evidence: Historical funding was $68,000 ADA; current budget is $952,750 ADA. The historical proposal was not previously funded (status unknown/no), but the work described represents a foundational primitive that the current proposal seeks to build upon or replicate at scale.
- Relationship evidence: Different proposers (Five Binaries vs p-lido-38be30a8-07cc-49ab-87d9-904bd6aa9755); no shared organizational names or addresses.
- Review notes: The current proposal appears to be a significantly expanded iteration of the same core concept as the historical F15 project, likely driven by market demand rather than direct reuse of prior code. The overlap is high in functional scope (token streaming) but low in textual similarity, suggesting independent development or significant architectural evolution. Given the substantial budget increase and lack of proposer relationship, this represents a new proposal building on an established idea rather than duplicative work.
- Source: https://www.catalystexplorer.com/en/proposals/c-streaming-protocol-real-time-continuous-payment-standard-f15

### Open Sourced RWA Tokenization Framework with Revenue Share Model

- Current proposer: Jose Velazquez
- Current requested budget: 1,339,000.00 ADA
- Triage matches: 3

#### Project Catalyst: Real Estate Tokenization Powered by Cardano

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: partial (no; 250,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 3, score 0.236, shared terms: compliance, development, estate, existing, kyc, real, rwa, smart, tokenization, use
- Overlap evidence: Both proposals target identical real-world use cases (Vierci Development real estate tokenization) with nearly identical technical approaches (CIP 68/113 for metadata and issuance), legal frameworks, and revenue models. The current proposal explicitly references the historical project's deployments as validation.
- Funding evidence: Historical proposal was unfunded but over budget; current proposal is a new submission with significantly higher funding ($1.3M vs $0.25M).
- Relationship evidence: Different proposers (Jose Velazquez vs p-lido-4036d1d6-d7e5-4398-9974-89c5c463a52b); historical proposer is a LIDO address, suggesting distinct entities.
- Review notes: The current proposal appears to be a direct expansion or re-submission of the historical work by a different entity, leveraging existing infrastructure and deployments rather than creating new work. The high overlap suggests the proposer is building upon previously conceptualized (but unfunded) work.
- Source: https://www.catalystexplorer.com/en/proposals/real-estate-tokenization-powered-by-cardano-f14

#### Project Catalyst: High-Yield RWA: Tokenized Real Estate  

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (no; 250,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 9, score 0.218, shared terms: compliance, development, estate, existing, kyc, real, rwa, smart, tokenization, tokenized
- Overlap evidence: identical partner (Vierci Development), identical use case (high yield real estate tokenization), identical technical approach (CIP 68/113 for metadata and issuance), identical revenue model (15% profit share to treasury), and identical deployment scope (Paraguay/Ecuador cattle feedlots)
- Funding evidence: historical proposal was previously funded with 250,000.00 ADA under Project Catalyst
- Relationship evidence: different proposer entities (Jose Velazquez vs p-lido-ff972555-916e-4d00-8795-530bd4d02f22)
- Review notes: The current proposal appears to be a direct expansion or re-proposal of the same work by a different entity. The core value proposition, partner, technical implementation, and deployment details are nearly identical to the historical F15 proposal. This suggests either a strategic reuse of infrastructure by Valoris or a continuation of the project under new leadership without significant innovation.
- Source: https://www.catalystexplorer.com/en/proposals/high-yield-rwa-tokenized-real-estate-f15

#### Project Catalyst: Cardano’s $10T Institutional RWA Tokenization Infrastructure

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (no; 750,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 1, score 0.283, shared terms: 113, assets, built, cip, compliance, compliant, fully, grade, growth, infrastructure
- Overlap evidence: Both proposals address institutional RWA tokenization infrastructure on Cardano using CIP 113 for programmable issuance and compliance. The current proposal expands this by adding CIP 68 for dynamic metadata and includes a specific revenue share model (15% to Treasury) with real-world deployment examples, whereas the historical proposal focused on general infrastructure building.
- Funding evidence: Historical funding was $750,000 ADA; current budget is $1,339,000 ADA. Historical status shows 'previously_funded: no' in metadata but text indicates F15 involvement suggesting potential prior activity or misclassification in the provided signal.
- Relationship evidence: Different proposers (Jose Velazquez vs p-lido-871d5ef1-1d8b-4dc4-8d1e-94e53b1c5eb7); different entities involved (Valoris vs Libertum/F15 Partners).
- Review notes: The proposals share a core theme of RWA infrastructure on Cardano via CIP 113, indicating medium overlap. The current proposal adds significant value through CIP 68 integration and a concrete revenue-sharing mechanism, moving beyond the historical scope of general infrastructure building. Proposers are unrelated entities.
- Source: https://www.catalystexplorer.com/en/proposals/cardanos-10t-institutional-rwa-tokenization-infrastructure-f15

### Oura by TxPipe: Maintaining Cardano’s Event Pipeline

- Current proposer: TxPipe
- Current requested budget: 540,750.00 ADA
- Triage matches: 3

#### Project Catalyst: Oura by TxPipe: going multi-chain

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 158,856.00 ADA)
- Proposer relationship: same
- Retrieval: rank 1, score 0.249, shared terms: across, development, events, oura, process, support, tool, txpipe
- Overlap evidence: The current proposal explicitly states Oura has been funded twice through Project Catalyst (Fund 9 and Fund 13), with F13 being the specific historical source. The work described in both proposals centers on maintaining the same Rust native pipeline tool (Oura) for Cardano events, expanding capabilities to multi-chain support previously, and ensuring reliability. The current proposal shifts focus from feature development to sustained maintenance and AI integration, which is a natural evolution of the previously funded core infrastructure.
- Funding evidence: Current budget: 540,750 ADA; Historical funding (F13): 158,856 ADA. The current proposal seeks to establish 'sustained maintenance coverage' for a project that has already received significant funding for development and multi-chain expansion.
- Relationship evidence: TxPipe is the recipient in both proposals; historical proposer addresses are associated with Lido but TxPipe is the consistent project owner and beneficiary.
- Review notes: The overlap is high because the proposal is essentially a continuation of the same project (Oura by TxPipe) receiving funding for its core maintenance function, which was previously funded under Project Catalyst. The shift from 'going multi-chain' to 'maintaining event pipeline' represents an evolution of the same work rather than new distinct work. The proposer relationship is confirmed as TxPipe in both cases.
- Source: https://www.catalystexplorer.com/en/proposals/oura-by-txpipe-going-multi-chain-f13

#### Project Catalyst: Pallas - Open-source maintainer

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: partial (yes; 143,571.00 ADA)
- Proposer relationship: different
- Retrieval: rank 5, score 0.202, shared terms: date, maintainer, months, multiple, native, pallas, part, protocol, rust, source
- Overlap evidence: Both proposals focus on maintaining a Rust-based open-source project using the Pallas library to ensure protocol compatibility. The historical proposal covered Pallas maintenance, while the current proposal covers Oura (which uses Pallas) and includes additional scope like AI documentation.
- Funding evidence: Historical funding was for 143,571 ADA over 6 months; current request is 420,000 ADA over 12 months. Historical work focused on Conway era protocol updates, whereas current work emphasizes general maintenance and AI integration.
- Relationship evidence: Historical proposer entities (p-lido-*) are distinct from current proposer (TxPipe), though both utilize the TxPipe team for execution.
- Review notes: The proposals share a core objective of maintaining Rust-based Cardano infrastructure (Pallas) but target different projects (Pallas vs Oura). The proposer relationship is indirect via the TxPipe team rather than direct identity. Overlap is significant in methodology and tooling but distinct in specific deliverables.
- Source: https://www.catalystexplorer.com/en/proposals/pallas-open-source-maintainer-f10

#### Project Catalyst: Oura v2

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 44,640.00 USD)
- Proposer relationship: different
- Retrieval: rank 12, score 0.186, shared terms: developer, development, event, feature, has, maintenance, oura, performance, source, that
- Overlap evidence: Both proposals address the same project 'Oura' and its core function as a Cardano event pipeline. The historical text requests bandwidth for new features and performance evolution, while the current proposal focuses on essential maintenance, bug fixing, and documentation. There is significant thematic overlap in maintaining the tool's stability and performance, but the scope differs (feature development vs. maintenance).
- Funding evidence: Historical funding was $44,640 USD for feature development; current request is $540,750 ADA (~$280k+ USD) for long-term maintenance. The historical project status is 'complete', indicating the specific versioning work is done, whereas the current proposal aims to establish ongoing operational coverage.
- Relationship evidence: Historical proposer names are Lido-related addresses (p-lido-...), while current proposer is TxPipe. Historical funding was for feature development and versioning; current proposal is for sustained maintenance of an existing stable tool.
- Review notes: The overlap is medium because while the subject matter (Oura event pipeline) and goals (maintainability/performance) are identical, the nature of the work has shifted from active feature development to passive maintenance. The proposers are unrelated entities (Lido vs TxPipe), suggesting a new entity taking over stewardship rather than a continuation of the original funding cycle.
- Source: https://www.catalystexplorer.com/en/proposals/oura-v2-f9

### Paid Open Source Model - Continued

- Current proposer: Open Source Committee (Intersect)
- Current requested budget: 4,601,000.00 ADA
- Triage matches: 5

#### On-chain TreasuryWithdrawals: Withdraw ₳5,885,000 for OSC Budget Proposal - Paid Open Source Model...

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: full (yes; 5,885,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 1, score 0.305, shared terms: across, advocacy, approval, available, based, blockchain, bounties, budget, bug, committee
- Overlap evidence: The current proposal is a continuation ('Continued') of the historical 'Paid Open Source Model'. Both address identical objectives: sustainable open source development, maintainer retainers, bug bounties, developer advocacy, and ecosystem stability. The current text references the activation of the model via a 2025 withdrawal, implying the historical proposal established the framework now being funded again.
- Funding evidence: The historical proposal (₳5.88M) was enacted to fund the initial implementation of the Paid Open Source Model. The current proposal (₳4.6M) is a subsequent withdrawal for continued execution, indicating the work package is not new but rather an extension of previously funded activities.
- Relationship evidence: Both proposals are submitted by Intersect on behalf of the Open Source Committee (OSC) and utilize the same organizational structure (Open Source Office). The historical proposal explicitly states it was sourced from an approved budget process administered by Intersect.
- Review notes: The proposals represent the same strategic initiative with the same proposer and recipient organization. The current proposal does not introduce new work types but rather continues the scope defined in the historical proposal. The overlap is substantial as the core objectives, target beneficiaries (maintainers, developers), and risk mitigation strategies are identical.
- Source: ipfs://bafkreiedjhlwerulq5qg5tku2qqremf2cf2dguxvktttnjddei3fxct37a

#### Treasury Fund 1: Open Source Committee - Developer Advocates Program, Committee Travel Budget, Bug Bounty

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 1,010,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 4, score 0.243, shared terms: across, advocate, attendance, available, budget, bug, committee, critical, delivery, developer
- Overlap evidence: Current proposal explicitly references the 'Paid Open Source Model' activation which was the subject of the historical proposal. Both cover Developer Advocates, Travel/Events, and Bug Bounties as core pillars. The current text states the historical work was a precursor to this continued funding model.
- Funding evidence: Historical amount: 1,010,000 ADA; Current amount: 4,601,000 ADA. Historical status 'contracted' indicates active execution of the core program components now being re-funded at a larger scale.
- Relationship evidence: Same proposer entity (Open Source Committee/Intersect), same historical proposal ID structure, identical milestone numbering scheme (10.x and 4.x referenced in both texts)
- Review notes: The current proposal is a direct continuation and expansion of the previously funded work. The historical proposal established the three main pillars (Advocates, Travel, Bug Bounties) which are explicitly restated as key objectives in the current text. The proposer is identical, and the work is not adjacent but rather an evolution of the same program structure.
- Source: https://treasury.sundae.fi/budgets/9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619/project/EC-0013(6,10,4)-25

#### On-chain TreasuryWithdrawals: IO: Developer Experience Initiative

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 3,601,926.00 ADA)
- Proposer relationship: same
- Retrieval: rank 16, score 0.199, shared terms: across, activity, additional, advocate, available, based, blockchain, bounties, budget, committee
- Overlap evidence: The current proposal ('Paid Open Source Model Continued') is a direct continuation and expansion of the historical 'Developer Experience Initiative'. Both focus on developer retention, tooling standardization (CLI, libraries), documentation unification, and bounty programs. The current proposal explicitly references the execution being contingent on the IntersectMBO budget approval, indicating it is the same work stream.
- Funding evidence: The historical funding of ~3.6M ADA established the infrastructure for developer experience improvements (tooling, bounties, documentation). The current proposal (~4.6M ADA) continues this mission with an expanded scope to include security risk mitigation and ecosystem stability, representing a logical progression rather than new work.
- Relationship evidence: Both proposals are led by the Open Source Committee (OSC) under Intersect; the historical proposal explicitly states collaboration with Intersect's Developer Advocate Program, which is the core component of the current proposal.
- Review notes: The current proposal is not new work but a continuation of the previously funded 'Developer Experience Initiative'. The overlap is substantial (>=60%) as the core objectives (developer retention, tooling, bounties) are identical. The proposer relationship is confirmed through explicit mentions of Intersect and the Developer Advocate Program in both texts.
- Source: ipfs://QmUnSimkwuaXX357ugYxDkiUMzsKTYgcWvV74xWbiXUt3Y

#### On-chain TreasuryWithdrawals: Cardano dOSPO and OMF Program

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: full (yes; 12,000,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 18, score 0.197, shared terms: across, additional, advocacy, always, andamio, approval, available, based, bounties, budget
- Overlap evidence: The current proposal ('Paid Open Source Model - Continued') is a direct continuation of the historical 'Cardano dOSPO and OMF Program'. The text explicitly references the previous program's components (Maintainer Retainer, Tooling Sustainability, Developer Advocates) and states the new model combines treasury governance with operational stewardship to solve limitations identified in the prior work. The current proposal covers all four pillars of the historical program: Maintenance Fund, Maintainer Development, CodeForUs bounties, and Ecosystem Activation.
- Funding evidence: The historical funding was 12M ADA over 36 months for a community-governed d(OSPO) model. The current proposal is 4.6M ADA over 18 months for the same entity (OSC/Intersect) to continue and refine this model, contingent on the approval of the Intersect MBO budget which funded the original structure.
- Relationship evidence: Proposer is Open Source Committee (Intersect), which directly evolved from the Intersect MBO team that built the original Paid Open Source Model. Christian Taylor explicitly states he departed Intersect to address structural problems in the previous model, and the current proposal is described as an evolution of lessons learned from the prior work.
- Review notes: This is a clear case of high-confidence overlap where the current proposal represents an evolution of previously funded work rather than new independent research. The proposer is the same organization (Intersect) that originally designed and partially funded the model, now operating under a slightly different governance structure (OSC vs Intersect MBO). The work covers nearly all components of the historical program with only minor structural refinements to address past operational friction.
- Source: ipfs://QmP76MXJwp19ZAcX8soUPyh5jcvMoK1DoLbxAJT9LLRhDK

#### Treasury Fund 1: OSC - Maintainer Retainer, Tooling Sustainability, Security Incident Management Programs

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 3,975,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 23, score 0.193, shared terms: across, andamio, approval, based, budget, committee, commonly, coordination, core, critical
- Overlap evidence: Current proposal continues the 'Paid Open Source Model' initiated in the historical proposal. Core objectives match exactly: Maintainer Retainer, Tooling Sustainability, and Security Incident Management. Historical text details specific milestones for these three pillars which are re-activated in the current proposal under similar strategic goals.
- Funding evidence: Historical funding of 3,975,000 ADA was contracted but paused; current proposal requests 4,601,000 ADA to continue and expand the same work packages (maintainers, tooling, security) over a new 18-month period.
- Relationship evidence: Same proposer entity (Open Source Committee/Intersect) and identical wallet address; historical proposal explicitly states execution is contingent on IntersectMBO budget approval.
- Review notes: This is a continuation of a previously funded program rather than new work. The historical proposal was paused but not cancelled, and the current proposal explicitly references the need for IntersectMBO budget approval to execute the same work packages. The overlap is substantial as the core deliverables (maintainer compensation, tooling maintenance, security coordination) are identical.
- Source: https://treasury.sundae.fi/budgets/9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619/project/EC-0013(1,2,7)-25

### Pallas by TxPipe: Maintaining Cardano's Core Rust Libraries, Year 2

- Current proposer: TxPipe
- Current requested budget: 540,750.00 ADA
- Triage matches: 3

#### Project Catalyst: Pallas - Open-source maintainer

- Match confidence: high
- Estimated current-work overlap: 95%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 143,571.00 ADA)
- Proposer relationship: same
- Retrieval: rank 1, score 0.267, shared terms: collection, date, era, maintainer, months, ouroboros, pallas, part, projects, protocol
- Overlap evidence: The current proposal continues the exact same open-source maintenance initiative for Pallas, expanding duration from 6 months to 12 months and adding AI documentation scope while maintaining identical core responsibilities (dependency updates, protocol compatibility, bug fixing). The historical text describes the project as an 'expanding collection of modules' requiring a maintainer to keep it up to date, which matches the current description of Pallas as a collection of Rust crates re-implementing core primitives.
- Funding evidence: The current proposal explicitly references 'continuing the open source maintenance initiative funded through Intersect's treasury process in the previous cycle' and states the new period begins after the closure of the existing contract, confirming continuity of funding for the same work.
- Relationship evidence: TxPipe is explicitly named as the assignee in the historical proposal and is the sole proposer of the current proposal; the historical text specifies assigning a 'Rust dev from the TxPipe team'.
- Review notes: This is a direct continuation of previously funded work by the same organization (TxPipe) for the exact same project (Pallas). The proposal seeks to extend the duration and slightly expand scope rather than introduce new work. No additional overlap assessment is needed as the work is identical in nature and origin.
- Source: https://www.catalystexplorer.com/en/proposals/pallas-open-source-maintainer-f10

#### On-chain TreasuryWithdrawals: Withdraw ₳220,914 for Pallas: Sustaining Critical Rust Tooling for Cardano

- Match confidence: high
- Estimated current-work overlap: 95%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 220,914.00 ADA)
- Proposer relationship: same
- Retrieval: rank 3, score 0.247, shared terms: across, actively, address, aiken, amaru, broader, bug, building, cbor, collaboration
- Overlap evidence: The historical text explicitly states Pallas provides 'reusable components, such as cryptographic primitives and CBOR encoding' used by projects like Aiken, Lucid, Mithril, and Amaru. The current proposal confirms these exact same crates serve as shared infrastructure for the identical list of downstream projects (Aiken, Dolos, Lucid, Oura, Mithril, Amaru). Both proposals outline the need for ongoing maintenance, bug fixing, dependency updates, and protocol compatibility.
- Funding evidence: The current proposal requests 420,000 ADA to fund a part-time maintainer over 12 months. The historical proposal requested 220,914 ADA for a similar role (0.5 FTE developer + 0.125 FTE tech lead) to sustain the same critical tooling. The current proposal is an extension of the previous funding cycle.
- Relationship evidence: Both proposals are for the exact same project (Pallas by TxPipe), managed by the same vendor (TxPipe/Intersect), and describe identical core responsibilities (maintaining Rust crates for Cardano primitives like CBOR and cryptography). The current proposal is a direct continuation of the previous contract.
- Review notes: This is a clear case of work continuity rather than new work. The proposer (TxPipe) is the same entity managing the project in both cycles. The historical withdrawal was enacted based on an approved vendor budget, and the current proposal continues this specific engagement without introducing new domains or significant scope changes.
- Source: ipfs://bafkreigm5xreg7ezyedhowwecyy2qnue3bfhbw5dex5odmvunddeg5jsem

#### Project Catalyst: SIDAN - Whisky V2 - Cardano Rust SDK with Pallas

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 74,000.00 ADA)
- Proposer relationship: same
- Retrieval: rank 8, score 0.206, shared terms: broader, core, dependency, pallas, public, rust, support, txpipe
- Overlap evidence: The current proposal describes maintaining Pallas (Rust crates for core primitives) which serves as infrastructure for projects like Whisky. The historical proposal explicitly states that 'Moving to TxPipe's pallas' is the solution to improve maintainability and feature support for Whisky, confirming the work is identical in nature (maintaining the same Rust SDK).
- Funding evidence: The current proposal continues a maintenance initiative funded through Intersect's treasury process in the previous cycle, with the historical record showing an approved funding status for the related project.
- Relationship evidence: Current proposer 'TxPipe' is explicitly named as the entity moving to in the historical proposal text ('Moving to TxPipe's pallas'), indicating a direct organizational relationship or identity.
- Review notes: The current proposal is a direct continuation of the work described in the historical proposal. The proposer 'TxPipe' is the same entity referenced in the historical text as the provider of Pallas. The work covers the exact same scope: maintaining the Cardano Rust SDK (Pallas) to support downstream projects like Whisky. The overlap is substantial, not merely adjacent.
- Source: https://www.catalystexplorer.com/en/proposals/sidan-whisky-v2-cardano-rust-sdk-with-pallas-f14

### Project Janus: A Roadmap to Decentralized Bridge Authorization and Generalized Cross-Chain Messaging

- Current proposer: ChainPort (by DcentraLab)
- Current requested budget: 30,570,400.00 ADA
- Triage matches: none.

### Security Threat Assessment Guard (STAG): Continuous Security Assurance for the Cardano Ecosystem

- Current proposer: Ensurable Systems Ltd
- Current requested budget: 7,890,487.00 ADA
- Triage matches: none.

### The Marketing Powered Demand Engine for Cardano

- Current proposer: Serviceplan Group
- Current requested budget: 20,871,418.00 ADA
- Triage matches: none.

### Tx3 by TxPipe: Open API Layer for Cardano's dApp Protocols

- Current proposer: TxPipe
- Current requested budget: 1,684,050.00 ADA
- Triage matches: 1

#### Project Catalyst: by TxPipe - API Layer for Cardano protocols using Tx3

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 23,500.00 ADA)
- Proposer relationship: different
- Retrieval: rank 1, score 0.355, shared terms: api, composability, dapp, development, intents, interface, layer, protocols, standardized, transaction
- Overlap evidence: Current proposal expands upon the foundational API layer concept introduced in the historical proposal, adding an agent-first documentation layer and MCP server capabilities to the existing protocol interface framework.
- Funding evidence: Historical funding (23,500 ADA) covered initial development of the Tx3 language and basic protocol mapping; current funding (1,684,050 ADA) targets scaling this infrastructure with 12 new onboardings and agent integration features.
- Relationship evidence: Different proposer entities (TxPipe vs p-lido-709b9590-242a-4c1f-8d67-6c085643dc3e) with low similarity score (0.122), though TxPipe is the active recipient of the current proposal.
- Review notes: The historical proposal established the core Tx3 API layer concept which is being expanded in the current proposal. While the proposers are distinct entities, the work builds directly on the previously funded foundation rather than duplicating it. The overlap is significant but not total, as the current scope includes new agent-specific features and scaling efforts.
- Source: https://www.catalystexplorer.com/en/proposals/by-txpipe-api-layer-for-cardano-protocols-using-tx3-f14

### UTxO RPC by TxPipe: Maintaining Cardano’s Integration Standard, Year 2

- Current proposer: TxPipe
- Current requested budget: 540,750.00 ADA
- Triage matches: 4

#### On-chain TreasuryWithdrawals: Withdraw ₳220,914 for UTxO RPC: Sustaining Cardano Blockchain Integration

- Match confidence: high
- Estimated current-work overlap: 95%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 220,914.00 ADA)
- Proposer relationship: same
- Retrieval: rank 1, score 0.297, shared terms: across, actively, adopted, amaru, based, been, blockchain, blockchains, communication, contract
- Overlap evidence: Both proposals describe the exact same project (UTxO RPC), identical goals (standardizing UTxO blockchain interactions via SDKs), and identical scope (maintenance, documentation, community support). The current proposal is explicitly described as 'continuing the open source maintenance initiative funded through Intersect's treasury process in the previous cycle'.
- Funding evidence: Current proposal requests 420,000 ADA for a part-time maintainer over 12 months; Historical proposal requested 220,914 ADA for similar roles (0.5 FTE developer + 0.125 FTE tech lead) to sustain the same project.
- Relationship evidence: Proposer name is identical (TxPipe); Historical text explicitly states 'TxPipe is an active member of the Cardano ecosystem' and references their 3+ years of development; Current proposal continues the initiative funded by Intersect on behalf of TxPipe.
- Review notes: This is a direct continuation of previously funded work by the same vendor. The current proposal represents an expansion or renewal of the UTxO RPC maintenance contract, not new independent work. The overlap is substantial as it covers the entirety of the project's core function and scope.
- Source: ipfs://bafkreibcranrq3y5eh7pcjuvq2tcmlapfw2pc7x3nazwp5lonx6docoayu

#### Project Catalyst: Cardano Node API: a Cardano Node companion written in Go

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 185,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 5, score 0.203, shared terms: compatibility, contract, data, developers, driven, multiple, node, over, protocol, through
- Overlap evidence: Current proposal defines UTxO RPC as an open interface standard with Protocol Buffers and SDKs in multiple languages (including Go), adopted by Amaru, Dingo, and Haskell Cardano. Historical proposal sought to develop a 'Cardano Node API application in Golang' using a 'community driven communications protocol'. The historical text explicitly states the protocol is 'shared with TxPipe Dolos', confirming the work is identical or substantially reused.
- Funding evidence: Historical funding of 185,000 ADA supported the development of the Go-based API/protocol. Current proposal requests 420,000 ADA for maintenance and expansion of this exact standard (UTxO RPC) over a longer period, indicating continuity rather than new work.
- Relationship evidence: Historical proposer addresses are distinct from TxPipe; however, historical text explicitly mentions 'TxPipe Dolos' as the recipient of the shared protocol specification.
- Review notes: The current proposal is essentially a Year 2 maintenance contract for the same core infrastructure defined in the historical project. The overlap is high because the 'work' is the UTxO RPC specification itself, which was created and funded historically. The proposer change is expected as the original developers (Lido addresses) likely handed off maintenance to TxPipe, who are explicitly named in the historical text.
- Source: https://www.catalystexplorer.com/en/proposals/cardano-node-api-a-cardano-node-companion-written-in-go-f11

#### Treasury Fund 1: TxPipe - Pallas, UTxO RPC, Dolos

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 662,742.00 ADA)
- Proposer relationship: same
- Retrieval: rank 8, score 0.196, shared terms: based, blockchain, blockchains, core, data, designed, improvements, integration, interactions, interface
- Overlap evidence: Current proposal focuses exclusively on UTxO RPC maintenance, which was a primary component of the historical proposal covering Pallas, UTxO RPC, and Dolos. The current text describes identical maintenance activities (dependency updates, bug fixing, documentation) for the same specification previously funded.
- Funding evidence: Current budget is approximately 540k ADA vs historical total of 662k ADA; historical funding covered Pallas, UTxO RPC, and Dolos, while current proposal covers only UTxO RPC maintenance as a continuation of the previous contract.
- Relationship evidence: Proposer name 'TxPipe' matches historical recipient address associated with TxPipe projects; continuity of maintenance role explicitly stated in current text referencing previous cycle funding.
- Review notes: This appears to be a direct renewal/continuation of previously funded work by the same entity. The scope has narrowed from three projects (Pallas, UTxO RPC, Dolos) to one (UTxO RPC), but the core maintenance activities described are identical to those in the historical proposal. No new distinct work is proposed; it is a continuation of existing obligations.
- Source: https://treasury.sundae.fi/budgets/9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619/project/EC-0006-25,EC-0007-25,EC-0010-25

#### Project Catalyst: Andamio SDK & UTxO-RPC client

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 105,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 23, score 0.181, shared terms: developers, integration, rpc, sdks, treasury, utxo
- Overlap evidence: Current proposal explicitly continues the 'open source maintenance initiative' from the historical cycle, covering identical core tasks (dependency updates, protocol compatibility, bug fixing, documentation) for the same artifact (UTxO RPC). The current proposal adds AI integration scope, but the foundational work is a direct continuation of the previous funding.
- Funding evidence: Previous funding was $105,000 ADA; current request is $420,000 ADA for a part-time maintainer over 12 months, indicating a significant scale-up rather than new work.
- Relationship evidence: Different proposers (TxPipe vs p-lido-8dcf1911-0581-41aa-b30f-73848f4e4b41) with no apparent organizational link.
- Review notes: The proposal represents a continuation of previously funded work by a different entity. While the proposer is unrelated, the scope is not additive in terms of foundational maintenance but rather an expansion of resources for the same standard. The overlap is high because the core deliverable and maintenance tasks are identical to the historical project.
- Source: https://www.catalystexplorer.com/en/proposals/andamio-sdk-utxo-rpc-client-f13

### Wormhole Cross-Chain Infrastructure for Cardano: Institutional RWAs, Native Multichain Stablecoins

- Current proposer: Wormhole Foundation
- Current requested budget: 20,600,000.00 ADA
- Triage matches: 2

#### On-chain TreasuryWithdrawals: Withdraw ₳70,000,000 for Cardano Critical Integrations Budget

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: none (yes; 70,000,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 8, score 0.170, shared terms: active, administrator, approval, auditable, base, blockchains, bridge, capabilities, chain, commits
- Overlap evidence: Both proposals target cross-chain infrastructure, stablecoin integration, and institutional RWA onboarding. Historical text explicitly lists 'cross chain bridges' and 'tier one stablecoins' as critical integrations funded by the previous withdrawal, which aligns with the current proposal's focus on Wormhole's bridge and swap flows.
- Funding evidence: Historical funding of ₳70,000,000 ADA was allocated to a strategic integration fund for 'cross chain bridges' and 'stablecoin infrastructures'. Current proposal requests ₳20,600,000.00 ADA specifically for Wormhole's cross-chain infrastructure.
- Relationship evidence: Current proposer is Wormhole Foundation; historical proposal was driven by Input Output Global, Cardano Foundation, EMURGO, Midnight Foundation, and Intersect.
- Review notes: The current proposal appears to be a specific execution of the broad scope defined in the historical funding action. While the historical text mentions 'cross chain bridges' and 'stablecoin infrastructures' as key components funded by Intersect and IOG, the current proposal is from Wormhole Foundation, a distinct entity not listed as a primary driver in the historical text (though they may be partners). The overlap is significant regarding the *type* of work (bridges/stablecoins) but low on direct textual or proposer similarity. The historical funding covered multiple vendors confidentially, whereas this proposal names Wormhole specifically.
- Source: ipfs://bafkreiecqskxkmakkrzrs2xs2olh5jcwbuz5qr5gesp6merwcaydcaojiq

#### Project Catalyst: Ethereum to Cardano Multi-Asset Bridge Powered by Wormhole

- Match confidence: medium
- Estimated current-work overlap: 45%
- Overlap type: adjacent_related
- Previously proposed: True
- Previously funded relevance: partial (no; 750,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 11, score 0.168, shared terms: bridge, case, fee, liquidity, partners, wormhole
- Overlap evidence: Both proposals address Ethereum to Cardano bridging via Wormhole infrastructure. Historical proposal focused on basic multi-asset transfer; current proposal expands scope to institutional RWAs, native stablecoins (mUSD, USDS), and fee-based revenue models. Core bridge functionality is reused but significantly enhanced.
- Funding evidence: Historical proposal was unfunded and over budget. Current proposal seeks fresh funding for an evolved use case with higher budget ($20.6M vs $750k).
- Relationship evidence: Different proposers (Wormhole Foundation vs p-lido); Lido is a major Wormhole partner but not the same entity.
- Review notes: The current proposal builds upon the foundational bridge concept from the historical proposal but targets a broader institutional market with distinct revenue mechanisms. While the core technology (Wormhole bridge) is reused, the scope and objectives have shifted significantly enough to warrant medium confidence rather than high confidence.
- Source: https://www.catalystexplorer.com/en/proposals/ethereum-to-cardano-multi-asset-bridge-powered-by-wormhole-f14

### zkFold Open Source Cardano Infrastructure 2026

- Current proposer: zkFold
- Current requested budget: 1,256,600.00 ADA
- Triage matches: 1

#### On-chain TreasuryWithdrawals: Withdraw ₳1,161,000 for zkFold ZK Rollup administered by Intersect

- Match confidence: high
- Estimated current-work overlap: 85%
- Overlap type: same_work
- Previously proposed: True
- Previously funded relevance: none (yes; 1,161,000.00 ADA)
- Proposer relationship: different
- Retrieval: rank 24, score 0.192, shared terms: all, build, chain, contract, cost, dapp, dapps, delivery, developers, enable
- Overlap evidence: current proposal explicitly states 'continue from the working testnet prototype' for ZK Rollup; historical text confirms zkFold team developed and implemented ZK rollups on Cardano via a previous funded project
- Funding evidence: historical withdrawal of 1,161,000 ADA specifically for zkFold ZK Rollup administered by Intersect; current proposal budget is 1,256,600 ADA for the same workstream
- Relationship evidence: different proposer entities (zkFold vs Intersect)
- Review notes: 
- Source: ipfs://bafkreigjofgwm4qtwn7r3e6nczaxo7jp4fmhzphozrpcuvnx5k2khlbtty
