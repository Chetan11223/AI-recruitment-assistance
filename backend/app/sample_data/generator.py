import os
from typing import List, Dict, Any
from app.parser.document_loader import ParsedDocument, DocumentPage
from app.parser.tree_builder import PageIndexTreeBuilder
from app.index.store import store
from app.index.schema import JobDescription

SAMPLE_RESUMES = [
    {
        "file_name": "alex_rivera_staff_backend.txt",
        "text": """ALEX RIVERA
San Francisco, CA | alex.rivera@example.com | (555) 234-5678 | github.com/alexrivera-eng

PROFESSIONAL SUMMARY
Staff Backend & Distributed Systems Engineer with over 9 years of experience architecting high-throughput, low-latency microservices. Deep expertise in Golang, Rust, Kafka event-streaming, Redis distributed caching, and Kubernetes cluster orchestration. Proven track record scaling platforms from 10k to 5M QPS.

TECHNICAL SKILLS
- Languages: Golang, Rust, Python, C++, SQL
- Infrastructure & Cloud: AWS, Kubernetes, Docker, Terraform, Helm
- Databases & Caching: PostgreSQL, Redis, Apache Cassandra, DynamoDB
- Streaming & Messaging: Apache Kafka, RabbitMQ, gRPC, REST APIs
- Architecture: Distributed Systems, Microservices, Event-Driven Architecture, High-Availability

PROFESSIONAL EXPERIENCE

Staff Distributed Systems Engineer | CloudScale Networks | 2021 – Present
- Architected and deployed next-generation edge event-routing engine in Go and Rust processing 4.2M events/sec with sub-5ms p99 latency.
- Led migration of 40+ legacy monolith services into Kubernetes-orchestrated microservices using gRPC and Kafka, reducing compute costs by 38%.
- Designed distributed multi-region caching layer utilizing Redis Enterprise and DynamoDB, improving cache hit rates from 72% to 98.4%.
- Mentored a distributed team of 12 senior engineers, establishing architectural review standards and CI/CD pipelines.

Senior Backend Engineer | Stripe / Fintech Systems | 2018 – 2021
- Spearheaded the core settlement engine handling $1.2B in monthly transaction volume with zero financial discrepancy.
- Implemented idempotent payment ledger service in Golang with PostgreSQL and distributed locking via Redis.
- Built automated failover mechanism across 3 AWS availability zones ensuring 99.999% system uptime SLA.

Software Engineer | HighPoint Analytics | 2015 – 2018
- Built high-speed ingestion data pipelines using Python, Kafka, and Cassandra storing 10TB+ telemetry daily.
- Optimized slow relational database queries, improving dashboard load times by 65%.

KEY PROJECTS
- DistriCache (Open Source): High-performance distributed in-memory key-value store with Raft consensus written in Rust. (3.2k GitHub stars)
- UltraEvent Router: Zero-copy event dispatcher in Golang benchmarking at 8M msgs/sec on commodity hardware.

EDUCATION
- B.S. in Computer Science | University of California, Berkeley | 2011 – 2015
"""
    },
    {
        "file_name": "elena_rostova_senior_ml_rag.txt",
        "text": """ELENA ROSTOVA
Seattle, WA | elena.rostova@example.com | (555) 876-5432 | huggingface.co/erostova

PROFESSIONAL SUMMARY
Senior Machine Learning & Generative AI Engineer with 6.5 years of industry experience specializing in LLMs, Agentic RAG systems, PyTorch, and scalable AI infrastructure. Passionate about structure-aware retrieval, embedding distillation, and real-time inference optimization.

TECHNICAL SKILLS
- Core ML/AI: PyTorch, TensorFlow, HuggingFace, Transformers, Scikit-Learn, LangChain, LlamaIndex
- Languages: Python, C++, TypeScript, SQL
- Vector & Retrieval: FAISS, Pinecone, Qdrant, Tree-based Indexes, Graph Search
- Deployment & Infra: FastAPI, Docker, Triton Inference Server, AWS SageMaker, Ray
- Specialties: LLM Fine-tuning (LoRA/QLoRA), Agentic RAG, Knowledge Graphs, Semantic Chunking

PROFESSIONAL EXPERIENCE

Senior Generative AI Engineer | Synthetix AI | 2022 – Present
- Designed and productionized an enterprise Agentic RAG platform serving 50k daily active enterprise users over 10M documents.
- Developed hybrid vector + structural tree retrieval engine decreasing hallucination rate by 42% on complex financial reports.
- Fine-tuned 8B and 70B parameter open-weights LLMs using LoRA/vLLM, reducing average inference latency from 1.2s to 240ms.
- Built multi-agent reasoning framework in Python & FastAPI with automated tool-calling and reflection loops.

Machine Learning Engineer | NovaSearch Labs | 2019 – 2022
- Engineered neural semantic search ranking pipeline replacing legacy Elasticsearch keyword matching, improving NDCG@10 by 24%.
- Trained bi-encoder and cross-encoder sentence transformer models in PyTorch on 500M query-document pairs.
- Scaled distributed vector indexing pipeline on AWS processing 100M embeddings daily.

AI Research Intern | Microsoft Research | 2018 – 2019
- Researched dense retrieval and knowledge-grounded dialogue generation. Published findings in ACL workshop.

KEY PROJECTS
- PageTree-RAG: Open-source hierarchical document indexing library for LLM agent navigation without embeddings.
- FastInference-Engine: Optimized TensorRT-LLM container for multi-GPU streaming generation with continuous batching.

EDUCATION
- M.S. in Computer Science (AI Specialization) | University of Washington | 2017 – 2019
- B.S. in Applied Mathematics & Statistics | University of Washington | 2013 – 2017
"""
    },
    {
        "file_name": "marcus_vance_fullstack_lead.txt",
        "text": """MARCUS VANCE
Austin, TX | marcus.vance@example.com | (555) 456-7890 | linkedin.com/in/marcusvance

PROFESSIONAL SUMMARY
Senior Full Stack Engineer & Technical Lead with 7 years of experience building modern, responsive web applications, enterprise dashboards, and real-time collaboration platforms. Expert in React, TypeScript, Next.js, Node.js, GraphQL, and Tailwind CSS.

TECHNICAL SKILLS
- Frontend: React, Next.js, TypeScript, JavaScript, Tailwind CSS, Redux Toolkit, Framer Motion
- Backend: Node.js, Express, FastAPI, Python, GraphQL, REST
- Databases: PostgreSQL, Prisma ORM, MongoDB, Redis
- Tools & Cloud: Docker, AWS, Git, Vercel, Vite, Webpack, Jest, Playwright

PROFESSIONAL EXPERIENCE

Lead Full Stack Engineer | Apex Digital Solutions | 2021 – Present
- Led engineering team of 8 full-stack engineers building modern B2B SaaS analytics dashboard handling 1M+ monthly pageviews.
- Architected scalable frontend in Next.js 14 and TypeScript with server-side rendering, reducing First Contentful Paint by 55%.
- Implemented real-time collaborative workspace using WebSockets and GraphQL subscriptions in Node.js.
- Standardized reusable UI design system with Tailwind CSS and Radix UI across 5 product teams.

Senior Frontend Engineer | Lumina Cloud | 2019 – 2021
- Re-architected legacy Angular codebase into modular React / TypeScript micro-frontends.
- Built interactive data visualization dashboards using Recharts and D3.js rendering 100k+ real-time telemetry nodes.
- Integrated automated End-to-End test suites with Playwright, elevating test coverage from 35% to 88%.

Software Engineer | BuildCraft Interactive | 2017 – 2019
- Developed responsive web interfaces using React, JavaScript, and CSS Modules.
- Built backend REST APIs in Python/Django connected to PostgreSQL.

KEY PROJECTS
- React-Tree-Canvas: High-performance canvas-based hierarchical tree visualizer for large document indexes.
- RapidDash-UI: Open-source React component library with accessible components and theme support.

EDUCATION
- B.S. in Computer Science | University of Texas at Austin | 2013 – 2017
"""
    },
    {
        "file_name": "priya_sharma_cloud_devops.txt",
        "text": """PRIYA SHARMA
New York, NY | priya.sharma@example.com | (555) 345-6789 | github.com/priyasharma-infra

PROFESSIONAL SUMMARY
DevOps & Cloud Platform Engineer with 5 years of experience automating cloud infrastructure, Kubernetes orchestration, and CI/CD pipelines. Strong proficiency in AWS, Terraform, Docker, Golang, and observability stacks.

TECHNICAL SKILLS
- Cloud Platforms: AWS, GCP, Azure
- Orchestration & Containers: Kubernetes, Docker, Helm, ArgoCD
- Infrastructure as Code: Terraform, CloudFormation, Ansible
- CI/CD & Automation: GitHub Actions, GitLab CI, Jenkins, Bash, Python
- Monitoring & Observability: Prometheus, Grafana, Datadog, OpenTelemetry
- Networking & Security: VPC, IAM, TLS, Istio Service Mesh, DNS

PROFESSIONAL EXPERIENCE

Senior Platform / DevOps Engineer | FinScale Technologies | 2022 – Present
- Managed multi-region EKS Kubernetes clusters hosting 150+ microservices on AWS with 99.99% availability.
- Automated 100% of infrastructure provisioning using Terraform and GitHub Actions, cutting environment setup time from 3 days to 15 minutes.
- Implemented GitOps deployment workflows using ArgoCD and Helm charts, supporting 80+ deployments per day.
- Reduced monthly AWS cloud infrastructure expenditures by $45,000 via spot instance orchestration and intelligent auto-scaling.

DevOps Engineer | CloudSphere Solutions | 2019 – 2022
- Built automated CI/CD pipelines for 25 backend applications in Python and Golang.
- Configured enterprise observability dashboards in Prometheus and Grafana with automated PagerDuty alerting.
- Managed container security vulnerability scanning using Trivy and Docker Scout.

KEY PROJECTS
- KubeCost-Optimizer: Kubernetes controller written in Golang that right-sizes resource requests based on historical CPU/Memory metrics.
- TF-Modular-AWS: Reusable Terraform modules for enterprise AWS VPC, EKS, and RDS setups.

EDUCATION
- B.Tech in Information Technology | National Institute of Technology | 2015 – 2019
- Certifications: AWS Certified Solutions Architect Professional, Certified Kubernetes Administrator (CKA)
"""
    },
    {
        "file_name": "david_chen_junior_data_scientist.txt",
        "text": """DAVID CHEN
Chicago, IL | david.chen@example.com | (555) 901-2345 | linkedin.com/in/davidchen-ds

PROFESSIONAL SUMMARY
Junior Data Scientist & Python Developer with 2.5 years of experience conducting statistical data analysis, machine learning modeling, and dashboard creation. Proficient in Python, SQL, Scikit-Learn, Pandas, and data visualization.

TECHNICAL SKILLS
- Programming: Python, SQL, R, Bash
- Data Science & ML: Scikit-Learn, Pandas, NumPy, Statsmodels, Matplotlib, Seaborn
- Databases & BI: PostgreSQL, MySQL, Tableau, PowerBI, Excel
- Frameworks: Flask, FastAPI, Streamlit, Git, Jupyter

PROFESSIONAL EXPERIENCE

Data Scientist & Analyst | Apex Market Insights | 2022 – Present
- Built customer churn prediction models using Scikit-Learn and XGBoost, achieving an ROC-AUC of 0.86.
- Extracted and transformed large transaction datasets using SQL and Pandas for executive KPI reporting.
- Created automated executive dashboards in Tableau and Streamlit tracking revenue cohorts and conversion funnels.
- Partnered with product managers to design A/B test experiments and analyze statistical significance.

Data Analyst Intern | Midwest Financial Analytics | 2021 – 2022
- Cleaned and prepared financial time-series data using Python and Pandas.
- Automated weekly reporting scripts in Python, saving 6 hours of manual spreadsheet work per week.

KEY PROJECTS
- RealEstate-Price-Predictor: End-to-end regression model with Streamlit interactive UI predicting housing prices.
- E-Commerce-Customer-Segmentation: K-Means clustering analysis of 50k shoppers to identify purchasing personas.

EDUCATION
- B.S. in Statistics & Data Analytics | University of Illinois Urbana-Champaign | 2018 – 2022
"""
    }
]

SAMPLE_JOBS = [
    {
        "title": "Staff Backend Engineer - Distributed Systems",
        "company": "NextGen Cloud Platforms",
        "min_yoe": 7.0,
        "must_have_skills": ["Golang", "Kubernetes", "Kafka", "Distributed Systems", "Redis", "AWS"],
        "preferred_skills": ["Rust", "gRPC", "PostgreSQL", "Terraform", "Microservices", "Docker"],
        "responsibilities": [
            "Architect and scale multi-region, high-throughput microservices handling millions of requests per second.",
            "Lead distributed systems design, data consistency strategies, and caching architectures.",
            "Drive Kubernetes infrastructure evolution and zero-downtime deployment pipelines.",
            "Mentor senior engineers and establish engineering best practices across the organization."
        ],
        "raw_text": """Job Title: Staff Backend Engineer - Distributed Systems
Company: NextGen Cloud Platforms
Location: Remote / Hybrid

About The Role:
We are seeking a Staff Backend & Distributed Systems Engineer to lead the architecture and scaling of our core streaming platform. You will be responsible for systems processing millions of events per second with strict latency and high availability SLAs.

Requirements:
- 7+ years of professional backend software engineering experience.
- Deep expertise in Golang, Rust, or modern backend systems languages.
- Proven experience with distributed systems architectures, event-driven design (Apache Kafka), and distributed caching (Redis).
- Hands-on experience operating microservices on Kubernetes and AWS.
- Strong track record of technical leadership, architectural design reviews, and mentorship.
"""
    },
    {
        "title": "Senior AI & Generative RAG Engineer",
        "company": "Cognitive AI Systems",
        "min_yoe": 5.0,
        "must_have_skills": ["Python", "PyTorch", "LLMs", "RAG", "FastAPI", "HuggingFace"],
        "preferred_skills": ["LangChain", "LlamaIndex", "Vector Databases", "Docker", "AWS", "LoRA"],
        "responsibilities": [
            "Design, optimize, and deploy production-grade Agentic RAG and vectorless retrieval pipelines.",
            "Fine-tune and serve open-source Large Language Models with low latency and high accuracy.",
            "Build robust multi-agent tool-calling and reasoning workflows.",
            "Collaborate with product and data engineering teams to benchmark and reduce hallucination."
        ],
        "raw_text": """Job Title: Senior AI & Generative RAG Engineer
Company: Cognitive AI Systems
Location: San Francisco, CA / Remote

About The Role:
Join our AI Research & Applications team to build the future of structure-aware document intelligence and Agentic RAG systems. You will work on cutting-edge retrieval, LLM orchestration, and scalable AI infrastructure.

Requirements:
- 5+ years of software/ML engineering experience with at least 2+ years in Generative AI / LLMs.
- Expertise in Python, PyTorch, HuggingFace Transformers, and FastAPI.
- Deep hands-on experience with Retrieval-Augmented Generation (RAG), vectorless/tree search, and agentic workflows.
- Experience deploying ML models to production with Docker and cloud platforms.
"""
    }
]

class SampleDataLoader:
    @classmethod
    def load_all_samples(cls) -> Dict[str, Any]:
        loaded_cands = []
        loaded_jobs = []

        # 1. Load Job Descriptions
        for job_data in SAMPLE_JOBS:
            job = JobDescription(
                title=job_data["title"],
                company=job_data["company"],
                raw_text=job_data["raw_text"],
                min_yoe=job_data["min_yoe"],
                must_have_skills=job_data["must_have_skills"],
                preferred_skills=job_data["preferred_skills"],
                responsibilities=job_data["responsibilities"],
                education_requirements=["Bachelor's or Master's degree in Computer Science or equivalent experience."]
            )
            store.add_job(job)
            loaded_jobs.append(job)

        # 2. Load Resumes
        for res_data in SAMPLE_RESUMES:
            full_text = res_data["text"]
            pages = [DocumentPage(page_number=1, text=full_text, char_start_offset=0)]
            parsed_doc = ParsedDocument(
                file_name=res_data["file_name"],
                file_type="txt",
                full_text=full_text,
                pages=pages
            )
            candidate_profile = PageIndexTreeBuilder.build_tree(parsed_doc)
            store.add_candidate(candidate_profile)
            loaded_cands.append(candidate_profile)

        return {
            "status": "success",
            "candidates_loaded": len(loaded_cands),
            "jobs_loaded": len(loaded_jobs),
            "candidate_names": [c.candidate_name for c in loaded_cands],
            "job_titles": [j.title for j in loaded_jobs]
        }
