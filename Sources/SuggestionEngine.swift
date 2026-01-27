import Foundation

struct ActionStep: Identifiable {
    let id = UUID()
    let step: Int
    let title: String
    let detail: String
}

struct Suggestion: Identifiable {
    let id = UUID()
    let icon: String
    let category: String
    let title: String
    let description: String
    let actions: [ActionStep]
}

struct SuggestionEngine {
    static let allSuggestions: [Suggestion] = [
        // Market Expansion
        Suggestion(icon: "globe.americas.fill", category: "Market Expansion",
                   title: "Enter the Middle East & North Africa Market",
                   description: "Leverage growing tech adoption in UAE, Saudi Arabia, and Egypt. Set up a regional office in Dubai's free zones to access a $25B+ innovation economy with favorable tax structures.",
                   actions: [
                       ActionStep(step: 1, title: "Research Free Zone Options", detail: "Compare Dubai Internet City, DIFC, and Abu Dhabi Global Market. Evaluate setup costs, visa quotas, and tax benefits for each zone."),
                       ActionStep(step: 2, title: "Attend GITEX Global Conference", detail: "Register for GITEX in Dubai—the region's largest tech event. Use it to network, gauge demand, and identify potential local partners."),
                       ActionStep(step: 3, title: "Hire a Regional Business Development Lead", detail: "Recruit someone with an existing network in GCC tech ecosystems. Prioritize candidates with government procurement experience."),
                       ActionStep(step: 4, title: "Localize Your Offerings", detail: "Adapt marketing materials and case studies to regional industries (oil & gas, real estate, logistics). Consider Arabic-language collateral."),
                       ActionStep(step: 5, title: "Secure a Pilot Client", detail: "Offer a discounted or pro-bono engagement to one marquee regional client. Use the case study to build credibility for paid engagements."),
                   ]),
        Suggestion(icon: "building.2.fill", category: "Market Expansion",
                   title: "Launch a Government & Public Sector Division",
                   description: "Pursue government contracts for digital transformation. Many municipalities need innovation consulting and technology modernization, often with multi-year contract stability.",
                   actions: [
                       ActionStep(step: 1, title: "Register on Government Procurement Portals", detail: "Create profiles on SAM.gov, state procurement sites, and relevant platforms. Ensure your business certifications (e.g., small business, minority-owned) are up to date."),
                       ActionStep(step: 2, title: "Get Relevant Certifications", detail: "Pursue FedRAMP, SOC 2, or StateRAMP certifications depending on your target. These are often prerequisites for government RFPs."),
                       ActionStep(step: 3, title: "Partner with an Existing Government Contractor", detail: "Team up as a subcontractor on an existing contract to learn the process and build past performance history."),
                       ActionStep(step: 4, title: "Hire a Capture Manager", detail: "Bring on someone experienced in government sales cycles—they understand RFP responses, compliance requirements, and relationship building."),
                   ]),
        Suggestion(icon: "map.fill", category: "Market Expansion",
                   title: "Expand into Southeast Asian Markets",
                   description: "Singapore, Vietnam, and Indonesia have booming tech sectors. Consider partnerships with local accelerators to reduce entry costs and gain market credibility.",
                   actions: [
                       ActionStep(step: 1, title: "Set Up a Singapore Entity", detail: "Incorporate in Singapore for its business-friendly environment, strong IP protection, and access to ASEAN markets. Use a corporate secretary service to streamline setup."),
                       ActionStep(step: 2, title: "Join a Local Accelerator or Incubator", detail: "Apply to programs like Entrepreneur First, BLOCK71, or Antler Singapore to access mentors, investors, and early customers."),
                       ActionStep(step: 3, title: "Attend Tech in Asia or SWITCH Conferences", detail: "These are the premier regional tech events. Sponsor a booth or speaking slot to build visibility among Southeast Asian tech leaders."),
                       ActionStep(step: 4, title: "Identify Local Delivery Partners", detail: "Partner with development firms in Vietnam or Indonesia for cost-effective delivery. Vet partners through pilot projects before scaling."),
                   ]),
        Suggestion(icon: "airplane.departure", category: "Market Expansion",
                   title: "Open a European Innovation Hub",
                   description: "Establish presence in Berlin, Amsterdam, or Lisbon to tap into EU funding programs (Horizon Europe) and access a skilled, multilingual talent pool.",
                   actions: [
                       ActionStep(step: 1, title: "Compare Hub Locations", detail: "Evaluate Berlin (deep tech), Amsterdam (enterprise), and Lisbon (cost-effective talent). Consider tax incentives, talent availability, and client proximity."),
                       ActionStep(step: 2, title: "Apply for EU Horizon Europe Grants", detail: "Identify relevant calls under Cluster 4 (Digital, Industry, Space). Partner with a European university or research institute to strengthen your application."),
                       ActionStep(step: 3, title: "Hire a Country Manager", detail: "Recruit a local leader who understands the regulatory environment, business culture, and has an existing enterprise network."),
                       ActionStep(step: 4, title: "Start with a Co-Working Presence", detail: "Use spaces like Factory Berlin or B.Amsterdam before committing to a lease. This keeps costs low while you validate market demand."),
                   ]),

        // Product & Service
        Suggestion(icon: "cpu.fill", category: "Product & Service",
                   title: "Build an AI-Powered Analytics Platform",
                   description: "Develop a SaaS product that helps businesses analyze operational data using AI. Recurring revenue from subscriptions can significantly increase company valuation.",
                   actions: [
                       ActionStep(step: 1, title: "Interview 20 Existing Clients", detail: "Ask what data challenges they face daily. Look for patterns—the most common pain point becomes your product's core use case."),
                       ActionStep(step: 2, title: "Build an MVP with One Core Feature", detail: "Focus on a single high-value analysis (e.g., churn prediction, anomaly detection). Use existing AI APIs (OpenAI, AWS Bedrock) to accelerate development."),
                       ActionStep(step: 3, title: "Launch a Beta Program", detail: "Offer 5-10 clients free access in exchange for feedback and testimonials. Iterate weekly based on their usage patterns."),
                       ActionStep(step: 4, title: "Define Pricing Tiers", detail: "Create 3 tiers: Starter (self-serve), Professional (with support), Enterprise (custom). Benchmark against competitors like Mixpanel, Amplitude, or Tableau."),
                       ActionStep(step: 5, title: "Hire a Product Manager", detail: "Bring on a PM with SaaS experience to own the roadmap, prioritize features, and drive adoption metrics."),
                   ]),
        Suggestion(icon: "iphone.gen3", category: "Product & Service",
                   title: "Create a Mobile-First Client Portal",
                   description: "Offer clients real-time dashboards, project tracking, and communication through a branded mobile app. This increases retention and differentiates from competitors.",
                   actions: [
                       ActionStep(step: 1, title: "Map the Client Journey", detail: "Document every touchpoint clients have with your team. Identify which interactions could be self-served through an app (status checks, approvals, messaging)."),
                       ActionStep(step: 2, title: "Choose a Cross-Platform Framework", detail: "Use React Native or Flutter to ship on iOS and Android simultaneously. This halves development cost compared to native apps."),
                       ActionStep(step: 3, title: "Build Core Features First", detail: "Start with project status dashboard, file sharing, and in-app messaging. Add invoicing and reporting in v2."),
                       ActionStep(step: 4, title: "Pilot with 3 Key Clients", detail: "Roll out to your most engaged clients first. Their feedback will shape the experience before a wider launch."),
                   ]),
        Suggestion(icon: "cloud.fill", category: "Product & Service",
                   title: "Launch Managed Cloud Services",
                   description: "Offer end-to-end cloud migration and management. Businesses increasingly need partners for AWS, Azure, or GCP infrastructure—this creates sticky, recurring revenue.",
                   actions: [
                       ActionStep(step: 1, title: "Get Cloud Partner Certifications", detail: "Become an AWS Partner, Azure Partner, or Google Cloud Partner. These programs provide leads, co-marketing funds, and technical resources."),
                       ActionStep(step: 2, title: "Build a Migration Playbook", detail: "Document a repeatable process for assessing, planning, and executing cloud migrations. Standardization lets you scale without senior engineers on every project."),
                       ActionStep(step: 3, title: "Hire 2-3 Cloud Engineers", detail: "Recruit engineers with multi-cloud experience and relevant certifications (AWS Solutions Architect, Azure Administrator). They'll deliver projects and train junior staff."),
                       ActionStep(step: 4, title: "Create Managed Service Packages", detail: "Offer monthly retainers for monitoring, security patching, cost optimization, and 24/7 support. Price based on infrastructure size and SLA level."),
                   ]),
        Suggestion(icon: "lock.shield.fill", category: "Product & Service",
                   title: "Add Cybersecurity Consulting Services",
                   description: "With rising cyber threats, offer security audits, penetration testing, and compliance consulting. This is a high-margin service with strong demand across all industries.",
                   actions: [
                       ActionStep(step: 1, title: "Hire a CISO-Level Consultant", detail: "Recruit a senior security professional with CISSP or CISM certification to lead the practice and lend credibility with enterprise clients."),
                       ActionStep(step: 2, title: "Define Service Packages", detail: "Offer tiered packages: Security Assessment ($5-15K), Penetration Test ($10-30K), Compliance Audit ($15-50K), and Managed Security (monthly retainer)."),
                       ActionStep(step: 3, title: "Get Compliance Certifications", detail: "Pursue SOC 2 Type II for your own company first. This proves you practice what you preach and is often a prerequisite for enterprise clients."),
                       ActionStep(step: 4, title: "Partner with a SIEM/MDR Vendor", detail: "Become a reseller for tools like CrowdStrike, SentinelOne, or Splunk. This adds product revenue on top of service fees."),
                   ]),
        Suggestion(icon: "wrench.and.screwdriver.fill", category: "Product & Service",
                   title: "Develop a No-Code/Low-Code Platform",
                   description: "Build tools that let non-technical users create workflows and apps. The no-code market is projected to grow rapidly, and it opens up an entirely new customer segment.",
                   actions: [
                       ActionStep(step: 1, title: "Identify a Niche Use Case", detail: "Don't compete with Bubble or Retool head-on. Pick a vertical (e.g., no-code for logistics, no-code for HR workflows) where you have domain expertise."),
                       ActionStep(step: 2, title: "Build a Drag-and-Drop Prototype", detail: "Use a visual builder framework to create a prototype. Focus on 5-10 pre-built components that solve 80% of your target users' needs."),
                       ActionStep(step: 3, title: "Launch a Free Tier", detail: "Offer a generous free plan to drive adoption. Convert users to paid plans when they need custom integrations, team features, or higher usage limits."),
                       ActionStep(step: 4, title: "Create Template Marketplace", detail: "Build 20-30 ready-made templates for common workflows. Users who start from templates activate faster and convert to paid plans at higher rates."),
                       ActionStep(step: 5, title: "Build a Community", detail: "Launch a Discord or forum for users to share templates, ask questions, and showcase what they've built. Community-led growth reduces customer acquisition costs."),
                   ]),

        // Partnerships & Channels
        Suggestion(icon: "person.3.fill", category: "Partnerships",
                   title: "Partner with Universities for R&D",
                   description: "Collaborate with university research labs to co-develop innovations. This provides access to cutting-edge research, talent pipelines, and potential grant funding.",
                   actions: [
                       ActionStep(step: 1, title: "Identify Target Research Labs", detail: "Look at CS, data science, and engineering departments at top universities near you. Review recent publications to find labs aligned with your focus areas."),
                       ActionStep(step: 2, title: "Propose a Sponsored Research Project", detail: "Offer $50-100K to fund a graduate research project relevant to your product roadmap. You get IP rights; the university gets funding and publications."),
                       ActionStep(step: 3, title: "Create an Internship Pipeline", detail: "Offer paid internships to grad students in the partner lab. This gives you first access to top talent before they hit the job market."),
                       ActionStep(step: 4, title: "Co-Apply for Government R&D Grants", detail: "NSF SBIR/STTR grants fund industry-university collaborations. Awards range from $250K to $1M+ and validate your technology."),
                   ]),
        Suggestion(icon: "link.circle.fill", category: "Partnerships",
                   title: "Build a Reseller & Affiliate Network",
                   description: "Recruit technology consultants and agencies as resellers. A channel partner program can scale revenue without proportionally scaling your sales team.",
                   actions: [
                       ActionStep(step: 1, title: "Design the Partner Program Structure", detail: "Define tiers (Silver, Gold, Platinum) with clear benefits: revenue share (20-40%), co-marketing funds, deal registration protection, and certification badges."),
                       ActionStep(step: 2, title: "Build a Partner Portal", detail: "Create a self-serve portal with sales collateral, demo environments, deal registration forms, and commission tracking dashboards."),
                       ActionStep(step: 3, title: "Recruit 10 Founding Partners", detail: "Reach out to complementary consultancies and agencies. Offer founding partners extra incentives (higher margins, exclusive territories) for early commitment."),
                       ActionStep(step: 4, title: "Create Partner Enablement Training", detail: "Build a 2-day certification course covering your products, sales methodology, and delivery process. Partners who are trained sell 3x more."),
                   ]),
        Suggestion(icon: "handshake.fill", category: "Partnerships",
                   title: "Form Strategic Alliance with a Big 4 Firm",
                   description: "Partner with Deloitte, PwC, EY, or KPMG as a specialized technology implementation partner. Their clients need niche tech expertise that large firms often outsource.",
                   actions: [
                       ActionStep(step: 1, title: "Identify the Right Practice Area", detail: "Research which Big 4 practice groups align with your expertise. Technology consulting, digital transformation, and innovation labs are the best entry points."),
                       ActionStep(step: 2, title: "Get Introduced Through Mutual Contacts", detail: "Use LinkedIn, alumni networks, or advisory board members to get warm introductions to practice leaders. Cold outreach rarely works with Big 4."),
                       ActionStep(step: 3, title: "Propose a Joint Pilot Project", detail: "Offer to co-deliver a project at a reduced rate to demonstrate your capabilities. Success on one project often leads to a preferred vendor relationship."),
                       ActionStep(step: 4, title: "Formalize the Alliance Agreement", detail: "Work with legal to define scope, revenue sharing, IP ownership, and non-compete boundaries. Push for a non-exclusive agreement to preserve flexibility."),
                   ]),
        Suggestion(icon: "graduationcap.fill", category: "Partnerships",
                   title: "Launch a Certified Partner Training Program",
                   description: "Train and certify external consultants on your methodologies. This extends your reach, builds an ecosystem, and creates an additional revenue stream from training fees.",
                   actions: [
                       ActionStep(step: 1, title: "Document Your Core Methodology", detail: "Codify your proprietary processes into a structured curriculum. Break it into modules that can be taught in 2-3 day sessions."),
                       ActionStep(step: 2, title: "Build a Certification Exam", detail: "Create a proctored assessment with practical and theoretical components. Certified partners should be able to deliver your methodology independently."),
                       ActionStep(step: 3, title: "Price the Certification", detail: "Charge $2,000-5,000 per certification with annual renewal fees of $500-1,000. Include access to updated materials and a partner directory listing."),
                       ActionStep(step: 4, title: "Launch with a Cohort Model", detail: "Run the first 2-3 cohorts yourself to refine the curriculum. Then train internal staff to deliver the program at scale."),
                   ]),

        // Revenue Model
        Suggestion(icon: "dollarsign.circle.fill", category: "Revenue Model",
                   title: "Introduce Outcome-Based Pricing",
                   description: "Shift from hourly billing to value-based pricing tied to measurable client outcomes (e.g., revenue growth, cost savings). This aligns incentives and supports premium pricing.",
                   actions: [
                       ActionStep(step: 1, title: "Identify Measurable Outcomes", detail: "Work with 2-3 clients to define success metrics: revenue increase, cost reduction, time saved, or conversion rate improvement. These become your pricing anchors."),
                       ActionStep(step: 2, title: "Create a Pricing Formula", detail: "Structure as base fee + performance bonus. Example: $50K base + 10% of documented cost savings above baseline. Cap the upside to manage client expectations."),
                       ActionStep(step: 3, title: "Pilot with One Engagement", detail: "Test the model on a single project. Document everything—what worked, what was hard to measure, and how the client perceived the value."),
                       ActionStep(step: 4, title: "Build a Value Calculator Tool", detail: "Create a spreadsheet or simple web tool that helps prospects estimate their ROI from working with you. This anchors pricing conversations around value, not cost."),
                   ]),
        Suggestion(icon: "arrow.triangle.2.circlepath", category: "Revenue Model",
                   title: "Create a Subscription Advisory Service",
                   description: "Offer a monthly retainer for ongoing innovation advisory. Clients get a set number of consulting hours, priority support, and quarterly strategy reviews.",
                   actions: [
                       ActionStep(step: 1, title: "Define 3 Retainer Tiers", detail: "Essential ($5K/mo, 10hrs + quarterly review), Professional ($12K/mo, 25hrs + monthly review), Enterprise ($25K+/mo, dedicated advisor + weekly sessions)."),
                       ActionStep(step: 2, title: "Convert Existing Project Clients", detail: "Approach clients whose projects are ending. Offer a transition to a retainer that includes ongoing support, strategic advice, and priority access for new projects."),
                       ActionStep(step: 3, title: "Build a Client Success Framework", detail: "Create onboarding templates, quarterly business review decks, and progress tracking dashboards. Systematize the advisory experience."),
                       ActionStep(step: 4, title: "Set a Retention Target", detail: "Aim for 90%+ annual retention. Track NPS scores, engagement metrics, and renewal rates. Assign a client success manager when you hit 10+ retainer clients."),
                   ]),
        Suggestion(icon: "chart.bar.fill", category: "Revenue Model",
                   title: "Monetize Data Insights & Benchmarking",
                   description: "Aggregate anonymized client data to produce industry benchmark reports. Sell these insights as a separate product or use them to attract inbound leads.",
                   actions: [
                       ActionStep(step: 1, title: "Audit Your Existing Data Assets", detail: "Catalog what anonymized data you've accumulated from client projects. Look for patterns in operational metrics, technology adoption, or performance benchmarks."),
                       ActionStep(step: 2, title: "Get Legal Sign-Off on Data Usage", detail: "Review client contracts for data usage rights. Update future contracts to include anonymized data aggregation permissions. Consult legal on GDPR/CCPA compliance."),
                       ActionStep(step: 3, title: "Produce a Pilot Benchmark Report", detail: "Create one high-quality report on a specific topic (e.g., 'State of Digital Transformation in Mid-Market Companies'). Gate it behind an email form for lead capture."),
                       ActionStep(step: 4, title: "Explore a Data-as-a-Service Model", detail: "If the data is valuable enough, offer API access or a dashboard for continuous benchmarking. Price at $500-2,000/month per subscriber."),
                   ]),

        // Talent & Operations
        Suggestion(icon: "person.badge.plus", category: "Talent & Ops",
                   title: "Build a Remote Global Talent Network",
                   description: "Hire specialized talent in lower-cost markets (Eastern Europe, Latin America) to scale delivery capacity while maintaining margins. Use async-first workflows.",
                   actions: [
                       ActionStep(step: 1, title: "Choose Target Regions", detail: "Eastern Europe (Poland, Ukraine, Romania) for deep engineering. Latin America (Argentina, Colombia, Mexico) for timezone alignment with US clients."),
                       ActionStep(step: 2, title: "Use an Employer of Record (EOR)", detail: "Services like Deel, Remote.com, or Oyster handle local compliance, payroll, and benefits. This lets you hire without setting up foreign entities."),
                       ActionStep(step: 3, title: "Hire a Remote Team Lead First", detail: "Recruit a senior person in the target region to lead hiring and culture-building locally. They'll attract better candidates through their network."),
                       ActionStep(step: 4, title: "Implement Async-First Processes", detail: "Document decisions in writing, record meetings, and use tools like Loom for updates. This ensures remote teams stay productive across time zones."),
                   ]),
        Suggestion(icon: "medal.fill", category: "Talent & Ops",
                   title: "Launch an Innovation Fellowship Program",
                   description: "Recruit top graduates for a 12-month fellowship combining client work with R&D projects. This builds your talent pipeline and generates fresh ideas.",
                   actions: [
                       ActionStep(step: 1, title: "Design the Fellowship Structure", detail: "Split time 70/30 between client work and R&D projects. Include mentorship from senior staff, monthly learning sessions, and a capstone presentation."),
                       ActionStep(step: 2, title: "Partner with 3-5 Target Universities", detail: "Build relationships with career services at top engineering, business, and design schools. Offer info sessions and campus presentations."),
                       ActionStep(step: 3, title: "Recruit the First Cohort of 4-6 Fellows", detail: "Run a competitive application process. Look for candidates with curiosity, initiative, and cross-disciplinary thinking—not just GPA."),
                       ActionStep(step: 4, title: "Create a Conversion Path", detail: "Offer full-time positions to top performers. Target a 60-70% conversion rate—this makes the fellowship your most effective recruiting channel."),
                   ]),
        Suggestion(icon: "gearshape.2.fill", category: "Talent & Ops",
                   title: "Automate Internal Operations with AI",
                   description: "Use AI to automate proposal generation, project scoping, and reporting. This frees up senior staff for billable work and reduces operational overhead by 20-30%.",
                   actions: [
                       ActionStep(step: 1, title: "Audit Time Spent on Non-Billable Work", detail: "Track how many hours per week your team spends on proposals, reports, admin, and internal meetings. Identify the top 3 time sinks."),
                       ActionStep(step: 2, title: "Automate Proposal Generation", detail: "Build a system that generates draft proposals from templates + past proposals using AI. Senior staff review and customize instead of writing from scratch."),
                       ActionStep(step: 3, title: "Automate Weekly Reporting", detail: "Connect project management tools to an AI system that generates client-ready status reports. Save 3-5 hours per project manager per week."),
                       ActionStep(step: 4, title: "Build an Internal Knowledge Base", detail: "Use RAG (Retrieval-Augmented Generation) to make past project learnings, methodologies, and templates searchable via natural language queries."),
                   ]),

        // Brand & Marketing
        Suggestion(icon: "megaphone.fill", category: "Brand & Marketing",
                   title: "Host an Annual Innovation Summit",
                   description: "Organize a flagship conference bringing together industry leaders, potential clients, and partners. Position Innovus-X as a thought leader and generate qualified leads.",
                   actions: [
                       ActionStep(step: 1, title: "Define the Event Format", detail: "Start with a 1-day, 150-200 person event. Mix keynotes, panels, and interactive workshops. Choose a theme that aligns with your positioning."),
                       ActionStep(step: 2, title: "Secure 3-5 Headline Speakers", detail: "Invite CTOs, VPs of Innovation, or founders from recognizable brands. Their names drive registrations. Offer speaker fees or equity-in-kind deals."),
                       ActionStep(step: 3, title: "Get Sponsors to Cover Costs", detail: "Offer sponsorship packages ($5K-25K) to technology vendors, cloud providers, and adjacent service firms. Aim to cover 80%+ of event costs through sponsors."),
                       ActionStep(step: 4, title: "Build a Lead Capture Strategy", detail: "Use registration data, session attendance, and post-event surveys to score leads. Have your sales team follow up with qualified prospects within 48 hours."),
                   ]),
        Suggestion(icon: "play.rectangle.fill", category: "Brand & Marketing",
                   title: "Launch a Podcast or Video Series",
                   description: "Create content featuring interviews with CTOs, founders, and innovation leaders. This builds brand authority, drives organic traffic, and nurtures prospects over time.",
                   actions: [
                       ActionStep(step: 1, title: "Choose Format and Cadence", detail: "Start with a bi-weekly podcast—lower production effort than video. Episodes of 25-35 minutes perform best. Pick a specific angle (e.g., 'How CTOs Make Build vs Buy Decisions')."),
                       ActionStep(step: 2, title: "Book Your First 10 Guests", detail: "Start with your network—clients, partners, advisors. Their participation lends credibility and they'll share episodes with their audiences."),
                       ActionStep(step: 3, title: "Set Up Production", detail: "Use Riverside.fm or Squadcast for remote recording. Hire a freelance editor ($100-200/episode). Create branded intro/outro and cover art."),
                       ActionStep(step: 4, title: "Distribute and Repurpose", detail: "Publish on Apple Podcasts, Spotify, YouTube. Turn each episode into 3-5 LinkedIn posts, a blog summary, and short video clips for social media."),
                   ]),
        Suggestion(icon: "doc.text.fill", category: "Brand & Marketing",
                   title: "Publish an Annual State of Innovation Report",
                   description: "Research and publish a comprehensive industry report. This becomes a lead magnet, earns media coverage, and establishes credibility with enterprise buyers.",
                   actions: [
                       ActionStep(step: 1, title: "Design a Survey", detail: "Create a 15-20 question survey targeting 200+ innovation and technology leaders. Use a mix of quantitative and qualitative questions to generate compelling data points."),
                       ActionStep(step: 2, title: "Distribute via Multiple Channels", detail: "Send to your email list, post on LinkedIn, partner with industry associations, and use paid promotion to hit your target response count."),
                       ActionStep(step: 3, title: "Hire a Designer for the Report", detail: "Invest $3-5K in professional design. Include data visualizations, executive summary, and pull quotes. A polished report gets shared and cited more."),
                       ActionStep(step: 4, title: "Launch with a PR Push", detail: "Write a press release highlighting 3-5 surprising findings. Pitch to industry publications and offer exclusive data to journalists for coverage."),
                       ActionStep(step: 5, title: "Gate the Full Report", detail: "Offer an ungated executive summary and gate the full report behind an email form. This balances reach with lead capture."),
                   ]),
        Suggestion(icon: "star.fill", category: "Brand & Marketing",
                   title: "Develop Client Case Study Library",
                   description: "Document detailed success stories with measurable outcomes. Case studies are the #1 content type B2B buyers use when evaluating vendors.",
                   actions: [
                       ActionStep(step: 1, title: "Select 5 High-Impact Projects", detail: "Choose projects with clear, quantifiable results (e.g., '40% cost reduction', '3x faster deployment'). Diverse industries strengthen your portfolio."),
                       ActionStep(step: 2, title: "Get Client Permission and Quotes", detail: "Ask clients for approval to publish. Interview a key stakeholder for a direct quote—named quotes are far more credible than anonymous ones."),
                       ActionStep(step: 3, title: "Follow a Standard Template", detail: "Use the Challenge → Approach → Results → Quote format. Keep each case study to 1-2 pages. Include specific metrics and a client logo."),
                       ActionStep(step: 4, title: "Integrate Into Sales Process", detail: "Add relevant case studies to proposals, your website, and sales decks. Train your team to reference specific case studies in prospect conversations."),
                   ]),

        // Vertical Specialization
        Suggestion(icon: "cross.case.fill", category: "Verticals",
                   title: "Specialize in HealthTech Innovation",
                   description: "Build deep expertise in healthcare technology—telemedicine, EHR integration, clinical AI. Healthcare IT spending exceeds $300B globally with strong growth.",
                   actions: [
                       ActionStep(step: 1, title: "Hire a Healthcare Domain Expert", detail: "Recruit someone with experience at a health system, health tech startup, or healthcare consultancy. Clinical credibility is essential in this market."),
                       ActionStep(step: 2, title: "Get HIPAA Compliance Certified", detail: "Complete HIPAA training for your team and implement compliant data handling processes. This is a non-negotiable requirement for healthcare clients."),
                       ActionStep(step: 3, title: "Attend HIMSS or HLTH Conferences", detail: "These are the premier healthcare tech events. Present a talk or host a booth to connect with health system CIOs and digital health startups."),
                       ActionStep(step: 4, title: "Build a HealthTech Reference Architecture", detail: "Create reusable solution blueprints for common health tech challenges (patient portals, clinical data integration, remote monitoring). This accelerates project delivery."),
                   ]),
        Suggestion(icon: "banknote.fill", category: "Verticals",
                   title: "Target FinTech & Banking Modernization",
                   description: "Help banks and financial institutions modernize legacy systems. Regulatory pressure and digital competition are driving massive technology spending in this sector.",
                   actions: [
                       ActionStep(step: 1, title: "Understand Regulatory Requirements", detail: "Study SOX, PCI DSS, and banking regulations in your target market. Compliance expertise is a key differentiator when selling to financial institutions."),
                       ActionStep(step: 2, title: "Build a Core Banking Modernization Playbook", detail: "Document a repeatable approach for migrating from legacy systems (COBOL, mainframes) to modern cloud-native architectures."),
                       ActionStep(step: 3, title: "Partner with a Banking Technology Vendor", detail: "Become an implementation partner for platforms like Temenos, Mambu, or Thought Machine. Vendor partnerships bring warm leads and co-selling support."),
                       ActionStep(step: 4, title: "Target Mid-Tier Banks and Credit Unions", detail: "Large banks use Big 4 consultancies. Mid-tier institutions ($1-50B in assets) need modernization but can't afford Accenture or McKinsey. That's your sweet spot."),
                   ]),
        Suggestion(icon: "leaf.fill", category: "Verticals",
                   title: "Enter the CleanTech & Sustainability Space",
                   description: "Advise companies on green technology adoption and ESG compliance. Sustainability consulting is growing 15%+ annually as regulations tighten worldwide.",
                   actions: [
                       ActionStep(step: 1, title: "Get ESG Reporting Expertise", detail: "Train your team on frameworks like GRI, SASB, and TCFD. Companies increasingly need help with mandatory ESG disclosures (SEC, EU CSRD)."),
                       ActionStep(step: 2, title: "Build a Carbon Footprint Assessment Service", detail: "Offer Scope 1, 2, and 3 emissions analysis for mid-market companies. Use established calculation methodologies and partner with carbon accounting platforms."),
                       ActionStep(step: 3, title: "Target Companies Facing New Regulations", detail: "Focus on companies affected by the EU CSRD, SEC climate disclosure rules, or California's SB 253. They have urgent compliance deadlines and budgets allocated."),
                       ActionStep(step: 4, title: "Develop a Sustainability Technology Roadmap Offering", detail: "Help companies identify which technologies (IoT sensors, energy management, supply chain traceability) will drive the most impact for their sustainability goals."),
                   ]),
        Suggestion(icon: "shippingbox.fill", category: "Verticals",
                   title: "Focus on Supply Chain & Logistics Tech",
                   description: "Help enterprises optimize supply chains with IoT, AI, and blockchain. Post-pandemic supply chain resilience is a top C-suite priority across industries.",
                   actions: [
                       ActionStep(step: 1, title: "Map Common Supply Chain Pain Points", detail: "Interview 10-15 supply chain leaders across industries. Focus on visibility gaps, demand forecasting failures, and supplier risk management."),
                       ActionStep(step: 2, title: "Build a Supply Chain Digital Twin Offering", detail: "Create a service that models a client's supply chain digitally, enabling scenario planning and risk simulation. Partner with platforms like Coupa or Kinaxis."),
                       ActionStep(step: 3, title: "Develop IoT Integration Capabilities", detail: "Build expertise in connecting sensors, RFID, and GPS tracking to supply chain management systems. Real-time visibility is the #1 client demand."),
                       ActionStep(step: 4, title: "Attend Gartner Supply Chain Symposium", detail: "This is where supply chain leaders go to find solutions. Present a case study or sponsor a session to position Innovus-X as a supply chain tech expert."),
                   ]),

        // Intellectual Property
        Suggestion(icon: "lightbulb.fill", category: "IP & Assets",
                   title: "Develop and License Proprietary Frameworks",
                   description: "Create branded innovation methodologies and license them to other consultancies. This generates passive income and strengthens brand recognition.",
                   actions: [
                       ActionStep(step: 1, title: "Codify Your Best Methodology", detail: "Take the process your team uses most successfully and formalize it into a named framework with defined stages, tools, and deliverables."),
                       ActionStep(step: 2, title: "Trademark the Framework Name", detail: "File a trademark application to protect your brand. A trademarked methodology commands higher licensing fees and prevents copycats."),
                       ActionStep(step: 3, title: "Create a Licensing Package", detail: "Bundle training materials, templates, certification exams, and brand guidelines. Price licenses at $10-25K/year per firm with tiered volume discounts."),
                       ActionStep(step: 4, title: "Recruit 5 Pilot Licensees", detail: "Offer early adopters a 50% discount for the first year in exchange for feedback and case studies. Use their success stories to sell to future licensees."),
                   ]),
        Suggestion(icon: "book.closed.fill", category: "IP & Assets",
                   title: "Create an Online Learning Academy",
                   description: "Build a platform offering courses on innovation, digital transformation, and emerging tech. Priced at $50-200/course, this scales without additional headcount.",
                   actions: [
                       ActionStep(step: 1, title: "Choose 3 Flagship Courses", detail: "Start with topics where you have deep expertise and market demand. Validate demand by surveying your email list or running a waitlist page."),
                       ActionStep(step: 2, title: "Record High-Quality Video Content", detail: "Invest in good audio (USB microphone), clean slides, and a structured curriculum. Each course should be 3-5 hours of content broken into 10-15 minute modules."),
                       ActionStep(step: 3, title: "Pick a Platform", detail: "Use Teachable, Thinkific, or Kajabi for hosting. These handle payments, progress tracking, certificates, and student management out of the box."),
                       ActionStep(step: 4, title: "Launch with a Founding Members Price", detail: "Offer the first 100 students a 50% discount. Their completion rates, reviews, and testimonials will fuel organic growth."),
                       ActionStep(step: 5, title: "Add Corporate Licensing", detail: "Offer bulk licenses for companies to train their teams. Price at $150-500/seat with custom branding and progress reporting for L&D departments."),
                   ]),
        Suggestion(icon: "hammer.fill", category: "IP & Assets",
                   title: "Build Open-Source Developer Tools",
                   description: "Release open-source tools that solve real developer problems. This builds community goodwill, attracts talent, and creates upsell opportunities for enterprise features.",
                   actions: [
                       ActionStep(step: 1, title: "Identify a Pain Point from Client Projects", detail: "Look for tools you've built internally that could be generalized. The best open-source projects solve a real problem the creator personally experienced."),
                       ActionStep(step: 2, title: "Release on GitHub with Good Documentation", detail: "Write a clear README with quick-start guide, API docs, and contributing guidelines. First impressions determine whether developers adopt your tool."),
                       ActionStep(step: 3, title: "Promote on Developer Communities", detail: "Share on Hacker News, Reddit (r/programming, r/webdev), Twitter/X, and relevant Discord/Slack communities. Write a launch blog post explaining the 'why.'"),
                       ActionStep(step: 4, title: "Build an Enterprise Version", detail: "Keep the core open-source. Add paid features like SSO, audit logs, SLA support, and advanced analytics. This is the proven open-core business model."),
                   ]),
    ]

    static func pickThree() -> [Suggestion] {
        var pool = allSuggestions
        var picked: [Suggestion] = []
        for _ in 0..<3 {
            if pool.isEmpty { break }
            let index = Int.random(in: 0..<pool.count)
            picked.append(pool.remove(at: index))
        }
        return picked
    }
}
