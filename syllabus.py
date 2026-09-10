"""
syllabus.py - Course Syllabus Curriculum & Active-Recall Question Bank
Strictly adheres to rule: ONLY the course syllabus structure is hardcoded as a dictionary.
All other entities (students, attendance, marks) reside dynamically in portal.db.
"""

from typing import Dict, Any, List, Optional

COURSE_SYLLABUS_DB: Dict[str, Dict[str, Any]] = {
    "CSE3001": {
        "course_code": "CSE3001",
        "course_title": "Software Engineering",
        "credits": 4,
        "modules": [
            {
                "module_id": 1,
                "title": "Software Process Models & Agile Methodologies",
                "exam_weightage": 15,
                "scope_topics": ["Waterfall vs Agile", "Scrum Framework", "Sprint Planning", "User Stories & Epics"],
                "tasks": [
                    {
                        "task_id": "CSE3001_M1_T1",
                        "title": "Master Sprint Burndown vs Burnup Chart Mechanics",
                        "weightage": 7,
                        "question": {
                            "prompt": "In an Agile Scrum framework, what does a burndown chart primarily visualize?",
                            "options": [
                                "The total velocity achieved across past releases",
                                "The remaining effort or work left in a sprint over time",
                                "The financial expenditure incurred per user story",
                                "The cumulative lines of code committed by developers"
                            ],
                            "correct_idx": 1,
                            "explanation": "A sprint burndown chart illustrates the outstanding remaining work (hours or story points) over the sprint timeline against the ideal burndown trajectory."
                        }
                    },
                    {
                        "task_id": "CSE3001_M1_T2",
                        "title": "Evaluate Requirements Elicitation & INVEST Criteria",
                        "weightage": 8,
                        "question": {
                            "prompt": "What does the 'E' stand for in the INVEST acronym for well-formed agile user stories?",
                            "options": [
                                "Executable",
                                "Estimable",
                                "Extendable",
                                "Exemplary"
                            ],
                            "correct_idx": 1,
                            "explanation": "INVEST stands for Independent, Negotiable, Valuable, Estimable, Small, and Testable."
                        }
                    }
                ]
            },
            {
                "module_id": 2,
                "title": "System Architecture & Structural UML Modeling",
                "exam_weightage": 15,
                "scope_topics": ["Class & Object Diagrams", "Package Diagrams", "Microservices vs Monoliths", "Layered Architecture"],
                "tasks": [
                    {
                        "task_id": "CSE3001_M2_T1",
                        "title": "Distinguish Composition from Aggregation in UML",
                        "weightage": 7,
                        "question": {
                            "prompt": "In UML class modeling, what indicates strong ownership where the child cannot exist without the parent (filled diamond)?",
                            "options": [
                                "Aggregation",
                                "Composition",
                                "Dependency",
                                "Generalization"
                            ],
                            "correct_idx": 1,
                            "explanation": "Composition is represented by a solid filled diamond and denotes strong 'has-a' lifecycle containment: if the container is destroyed, its parts perish too."
                        }
                    },
                    {
                        "task_id": "CSE3001_M2_T2",
                        "title": "Apply SOLID Design Principles to Architectural Refactoring",
                        "weightage": 8,
                        "question": {
                            "prompt": "Which SOLID principle states that higher-level modules should depend upon abstractions rather than concrete details?",
                            "options": [
                                "Single Responsibility Principle (SRP)",
                                "Liskov Substitution Principle (LSP)",
                                "Dependency Inversion Principle (DIP)",
                                "Open-Closed Principle (OCP)"
                            ],
                            "correct_idx": 2,
                            "explanation": "The Dependency Inversion Principle dictates that high-level policies should decouple from low-level details through abstract interfaces."
                        }
                    }
                ]
            },
            {
                "module_id": 3,
                "title": "Behavioral Modeling & State Machines",
                "exam_weightage": 20,
                "scope_topics": ["Sequence Diagrams", "Activity Diagrams", "State Machine Transitions", "Event Lifecycles"],
                "tasks": [
                    {
                        "task_id": "CSE3001_M3_T1",
                        "title": "Trace Synchronous vs Asynchronous Messages in Sequence Diagrams",
                        "weightage": 10,
                        "question": {
                            "prompt": "In a UML sequence diagram, what does an open arrow-head (stick arrowhead) designate?",
                            "options": [
                                "Synchronous call requiring return execution block",
                                "Asynchronous message where caller does not wait",
                                "Object instantiation lifeline termination",
                                "Conditional loop guard"
                            ],
                            "correct_idx": 1,
                            "explanation": "Stick/open arrowheads indicate non-blocking asynchronous message dispatch where the sender continues without waiting for an immediate acknowledgment."
                        }
                    },
                    {
                        "task_id": "CSE3001_M3_T2",
                        "title": "Construct Guard Conditions and State Invariants",
                        "weightage": 10,
                        "question": {
                            "prompt": "In a UML State Machine diagram, when is a transition triggered?",
                            "options": [
                                "Only when the enclosing composite state has no entry actions",
                                "When an event occurs and its boolean guard condition evaluates to true",
                                "Whenever an object's memory address changes",
                                "Exclusively during garbage collection sweeps"
                            ],
                            "correct_idx": 1,
                            "explanation": "State transitions execute when a triggering event fires and the associated guard predicate evaluates to true."
                        }
                    }
                ]
            },
            {
                "module_id": 4,
                "title": "Verification, Validation & Automated Testing Strategies",
                "exam_weightage": 25,
                "scope_topics": ["Unit & Integration Testing", "Equivalence Partitioning", "Boundary Value Analysis", "Mutation Testing"],
                "tasks": [
                    {
                        "task_id": "CSE3001_M4_T1",
                        "title": "Compute Cyclomatic Complexity using Mc Cabe's Graph Metric",
                        "weightage": 12,
                        "question": {
                            "prompt": "For a control flow graph with 14 edges (E), 10 nodes (N), and 1 connected component (P), what is the Cyclomatic Complexity V(G)?",
                            "options": [
                                "4",
                                "6",
                                "8",
                                "12"
                            ],
                            "correct_idx": 1,
                            "explanation": "V(G) = E - N + 2P = 14 - 10 + 2(1) = 6."
                        }
                    },
                    {
                        "task_id": "CSE3001_M4_T2",
                        "title": "Design Robust Test Cases via 2-Value Boundary Value Analysis",
                        "weightage": 13,
                        "question": {
                            "prompt": "If a valid input integer range is defined as 18 <= age <= 65, which values constitute robust boundary values?",
                            "options": [
                                "18 and 65 only",
                                "17, 18, 65, and 66",
                                "0, 18, 65, 100",
                                "Only middle values (30, 40, 50)"
                            ],
                            "correct_idx": 1,
                            "explanation": "Boundary Value Analysis tests on and immediately adjacent to boundaries: min-1 (17), min (18), max (65), and max+1 (66)."
                        }
                    }
                ]
            },
            {
                "module_id": 5,
                "title": "DevOps, CI/CD & Software Quality Assurance",
                "exam_weightage": 25,
                "scope_topics": ["Gitflow & Trunk-based Development", "Docker Containerization", "Automated Pipelines", "Static Analysis"],
                "tasks": [
                    {
                        "task_id": "CSE3001_M5_T1",
                        "title": "Architect Blue-Green vs Canary Production Deployments",
                        "weightage": 12,
                        "question": {
                            "prompt": "What is the key advantage of a Canary Deployment over standard recreate deployments?",
                            "options": [
                                "It requires completely shutting down the database tier",
                                "It routes a small percentage of live production traffic to the new version to detect faults safely",
                                "It eliminates the need for DNS load balancing",
                                "It doubles compute cost perpetually"
                            ],
                            "correct_idx": 1,
                            "explanation": "Canary deployment exposes a subset of real traffic to the new revision, allowing early metric validation with minimal blast radius."
                        }
                    },
                    {
                        "task_id": "CSE3001_M5_T2",
                        "title": "Integrate Static Quality Gates (SonarQube) into Build Pipelines",
                        "weightage": 13,
                        "question": {
                            "prompt": "What metric represents the estimated effort to remediate technical debt and code smells in static analysis?",
                            "options": [
                                "Remediation Cost Index",
                                "Technical Debt Ratio",
                                "Mutation Survival Rate",
                                "Churn Velocity"
                            ],
                            "correct_idx": 1,
                            "explanation": "The Technical Debt Ratio compares the cost of fixing issues to the total cost of rewriting the codebase."
                        }
                    }
                ]
            }
        ]
    },
    "CSE3002": {
        "course_code": "CSE3002",
        "course_title": "Database Management Systems",
        "credits": 4,
        "modules": [
            {
                "module_id": 1,
                "title": "Relational Data Modeling & Advanced SQL",
                "exam_weightage": 15,
                "scope_topics": ["ER to Relational Mapping", "Complex Subqueries", "Window Functions", "Common Table Expressions (CTEs)"],
                "tasks": [
                    {
                        "task_id": "CSE3002_M1_T1",
                        "title": "Master Window Functions (RANK vs DENSE_RANK)",
                        "weightage": 7,
                        "question": {
                            "prompt": "If values are [100, 100, 80], what will DENSE_RANK() assign to the third record (80)?",
                            "options": ["1", "2", "3", "NULL"],
                            "correct_idx": 1,
                            "explanation": "DENSE_RANK() leaves no gaps. Tied first place items both get 1, and the next item immediately receives rank 2."
                        }
                    },
                    {
                        "task_id": "CSE3002_M1_T2",
                        "title": "Convert Weak Entity Sets into Normal Form Relations",
                        "weightage": 8,
                        "question": {
                            "prompt": "What constitutes the primary key of a relation derived from a weak entity set?",
                            "options": [
                                "Its partial discriminator key alone",
                                "The primary key of its identifying owner plus its discriminator key",
                                "A surrogate auto-increment key only",
                                "Any candidate foreign key"
                            ],
                            "correct_idx": 1,
                            "explanation": "A weak entity set lacks a full primary key on its own; it requires the identifying parent's PK concatenated with its discriminator."
                        }
                    }
                ]
            },
            {
                "module_id": 2,
                "title": "Relational Algebra & Normalization Theory",
                "exam_weightage": 15,
                "scope_topics": ["Functional Dependencies", "1NF, 2NF, 3NF", "Boyce-Codd Normal Form (BCNF)", "Lossless Join Decomposition"],
                "tasks": [
                    {
                        "task_id": "CSE3002_M2_T1",
                        "title": "Execute Minimal Cover Algorithm for Functional Dependencies",
                        "weightage": 8,
                        "question": {
                            "prompt": "In BCNF, for every non-trivial functional dependency X -> Y, what condition must strictly hold?",
                            "options": [
                                "Y must be a prime attribute",
                                "X must be a superkey",
                                "X must contain at least two attributes",
                                "Y must not contain foreign keys"
                            ],
                            "correct_idx": 1,
                            "explanation": "BCNF requires that for every functional dependency X -> Y, the determinant X must be a superkey."
                        }
                    },
                    {
                        "task_id": "CSE3002_M2_T2",
                        "title": "Validate Dependency Preservation and Lossless Join Properties",
                        "weightage": 7,
                        "question": {
                            "prompt": "Under what condition is a binary decomposition of R into (R1, R2) guaranteed to be lossless?",
                            "options": [
                                "R1 intersection R2 is empty",
                                "(R1 ∩ R2) -> R1 or (R1 ∩ R2) -> R2",
                                "R1 union R2 contains exactly 5 columns",
                                "R1 has more rows than R2"
                            ],
                            "correct_idx": 1,
                            "explanation": "A decomposition is lossless if and only if the common attributes form a superkey of at least one of the decomposed relations."
                        }
                    }
                ]
            },
            {
                "module_id": 3,
                "title": "Transaction Processing & ACID Properties",
                "exam_weightage": 20,
                "scope_topics": ["Schedules & Serializability", "Conflict Serializability", "Two-Phase Locking (2PL)", "Deadlock Detection"],
                "tasks": [
                    {
                        "task_id": "CSE3002_M3_T1",
                        "title": "Analyze Conflict Serializability via Precedence Graphs",
                        "weightage": 10,
                        "question": {
                            "prompt": "A concurrent database schedule S is conflict serializable if and only if its precedence (serialization) graph:",
                            "options": [
                                "Contains at least one cycle",
                                "Is acyclic",
                                "Is a complete bipartite graph",
                                "Has equal in-degree and out-degree for all vertices"
                            ],
                            "correct_idx": 1,
                            "explanation": "Absence of cycles in the conflict serializability graph is the necessary and sufficient condition for conflict serializability."
                        }
                    },
                    {
                        "task_id": "CSE3002_M3_T2",
                        "title": "Enforce Strict Two-Phase Locking (Strict 2PL)",
                        "weightage": 10,
                        "question": {
                            "prompt": "What additional guarantee does Strict 2PL provide compared to standard 2PL?",
                            "options": [
                                "Guarantees no deadlocks will ever occur",
                                "Prevents cascading rollbacks by holding exclusive locks until transaction commit/abort",
                                "Eliminates all read locks",
                                "Allows dirty reads for higher throughput"
                            ],
                            "correct_idx": 1,
                            "explanation": "Strict 2PL holds exclusive locks until the end of the transaction, ensuring that uncommitted data cannot be read by other transactions and preventing cascading aborts."
                        }
                    }
                ]
            },
            {
                "module_id": 4,
                "title": "Indexing, B+ Trees & Query Optimization",
                "exam_weightage": 25,
                "scope_topics": ["B+ Tree Insertion & Deletion", "Clustered vs Secondary Indexes", "Cost-based Optimizer", "Hash Indexing"],
                "tasks": [
                    {
                        "task_id": "CSE3002_M4_T1",
                        "title": "Compute B+ Tree Fanout, Height, and Node Splitting",
                        "weightage": 12,
                        "question": {
                            "prompt": "Why are B+ trees preferred over standard B-trees for relational database storage engines?",
                            "options": [
                                "B+ trees hold all data pointers only in leaf nodes linked sequentially, optimizing range scans",
                                "B+ trees store duplicate keys across all internal nodes",
                                "B+ trees do not require disk balancing",
                                "B+ trees operate solely in RAM"
                            ],
                            "correct_idx": 0,
                            "explanation": "In a B+ tree, internal nodes store only routing keys, allowing high fanout, while linked leaf nodes make range scans extremely fast."
                        }
                    },
                    {
                        "task_id": "CSE3002_M4_T2",
                        "title": "Optimize Relational Query Execution Plans (EXPLAIN ANALYZE)",
                        "weightage": 13,
                        "question": {
                            "prompt": "In an EXPLAIN ANALYZE plan, what does a 'Sequential Scan' on a table with 10M rows typically indicate?",
                            "options": [
                                "The fastest possible indexed access path",
                                "Missing or unutilized index causing full table read from disk",
                                "A hash join with perfect bucket distribution",
                                "Zero I/O overhead"
                            ],
                            "correct_idx": 1,
                            "explanation": "A sequential scan reads every page of the table from disk, usually indicating the absence of an applicable index for the WHERE clause filter."
                        }
                    }
                ]
            },
            {
                "module_id": 5,
                "title": "Database Recovery & Distributed Data Architectures",
                "exam_weightage": 25,
                "scope_topics": ["ARIES Recovery Algorithm", "Write-Ahead Logging (WAL)", "Two-Phase Commit (2PC)", "CAP Theorem"],
                "tasks": [
                    {
                        "task_id": "CSE3002_M5_T1",
                        "title": "Trace ARIES Log Analysis, Redo, and Undo Phases",
                        "weightage": 12,
                        "question": {
                            "prompt": "What fundamental rule does Write-Ahead Logging (WAL) enforce?",
                            "options": [
                                "Data pages must be written to disk before log records are generated",
                                "The log record describing a change must be flushed to non-volatile storage before the corresponding dirty data page is written",
                                "Logs can be discarded once RAM usage reaches 90%",
                                "Transactions commit before writing anything to disk"
                            ],
                            "correct_idx": 1,
                            "explanation": "WAL guarantees atomicity and durability by ensuring that log records reach durable storage before dirty buffer pages are flushed."
                        }
                    },
                    {
                        "task_id": "CSE3002_M5_T2",
                        "title": "Coordinate Atomic Commits with Two-Phase Commit (2PC)",
                        "weightage": 13,
                        "question": {
                            "prompt": "In the 2PC protocol, what happens if any cohort node responds 'NO' (or times out) during Phase 1 (Prepare)?",
                            "options": [
                                "The coordinator commits the remaining nodes",
                                "The coordinator broadcasts a GLOBAL ABORT to all cohort nodes",
                                "The transaction retries automatically 10 times",
                                "The coordinator crashes intentionally"
                            ],
                            "correct_idx": 1,
                            "explanation": "If any participant votes NO or fails to respond in the prepare phase, the coordinator must abort the transaction globally to preserve atomicity."
                        }
                    }
                ]
            }
        ]
    },
    "CSE3003": {
        "course_code": "CSE3003",
        "course_title": "Computer Networks",
        "credits": 3,
        "modules": [
            {
                "module_id": 1,
                "title": "Physical Layer & Data Link Layer Fundamentals",
                "exam_weightage": 15,
                "scope_topics": ["OSI vs TCP/IP", "Framing & Error Detection", "CRC Polynomials", "Sliding Window Protocols"],
                "tasks": [
                    {
                        "task_id": "CSE3003_M1_T1",
                        "title": "Calculate Cyclic Redundancy Check (CRC) Checksum",
                        "weightage": 8,
                        "question": {
                            "prompt": "If a generator polynomial is of degree k, how many zero bits are appended to the data frame before modulo-2 division?",
                            "options": ["k - 1", "k", "k + 1", "2k"],
                            "correct_idx": 1,
                            "explanation": "In CRC, if the divisor polynomial degree is k, exactly k zeros are appended to the message bitstream."
                        }
                    }
                ]
            },
            {
                "module_id": 2,
                "title": "Medium Access Control & Ethernet Standards",
                "exam_weightage": 15,
                "scope_topics": ["CSMA/CD & CSMA/CA", "Binary Exponential Backoff", "VLANs", "ARP Protocol"],
                "tasks": [
                    {
                        "task_id": "CSE3003_M2_T1",
                        "title": "Analyze CSMA/CD Minimum Frame Size Requirements",
                        "weightage": 8,
                        "question": {
                            "prompt": "In CSMA/CD, what is the mandatory condition relating frame transmission time (T_tx) and round-trip propagation delay (RTT)?",
                            "options": ["T_tx < RTT / 2", "T_tx >= 2 * T_prop", "T_tx = 0", "T_tx <= T_prop"],
                            "correct_idx": 1,
                            "explanation": "To ensure collisions are detected before transmission completes, T_tx must be >= 2 * T_prop (or >= RTT)."
                        }
                    }
                ]
            },
            {
                "module_id": 3,
                "title": "Network Layer: Routing Algorithms & IP Addressing",
                "exam_weightage": 20,
                "scope_topics": ["IPv4 vs IPv6", "CIDR Subnetting", "Dijkstra OSPF", "Distance Vector BGP"],
                "tasks": [
                    {
                        "task_id": "CSE3003_M3_T1",
                        "title": "Execute CIDR Subnet Partitioning and Route Aggregation",
                        "weightage": 10,
                        "question": {
                            "prompt": "How many usable host IP addresses are available in a /27 IPv4 subnet?",
                            "options": ["32", "30", "64", "16"],
                            "correct_idx": 1,
                            "explanation": "A /27 subnet leaves 32 - 27 = 5 host bits. 2^5 = 32 addresses, minus 2 (network ID & broadcast) = 30 usable hosts."
                        }
                    }
                ]
            },
            {
                "module_id": 4,
                "title": "Transport Layer: TCP Congestion Control & Flow Mechanics",
                "exam_weightage": 25,
                "scope_topics": ["TCP 3-Way Handshake", "Slow Start & Congestion Avoidance", "Fast Retransmit (3 Dup ACKs)", "UDP vs TCP"],
                "tasks": [
                    {
                        "task_id": "CSE3003_M4_T1",
                        "title": "Trace TCP Reno Congestion Window Transitions",
                        "weightage": 12,
                        "question": {
                            "prompt": "In TCP Reno, what happens to cwnd and ssthresh upon receiving 3 duplicate ACKs?",
                            "options": [
                                "cwnd resets to 1 MSS, ssthresh unchanged",
                                "ssthresh = cwnd/2, cwnd = ssthresh + 3 MSS (Fast Recovery)",
                                "Both cwnd and ssthresh reset to zero",
                                "Connection is terminated immediately"
                            ],
                            "correct_idx": 1,
                            "explanation": "Upon 3 duplicate ACKs, TCP Reno initiates Fast Retransmit & Fast Recovery, setting ssthresh to cwnd/2 and cwnd to ssthresh + 3 MSS."
                        }
                    }
                ]
            },
            {
                "module_id": 5,
                "title": "Application Layer Protocols & Network Security",
                "exam_weightage": 25,
                "scope_topics": ["DNS Hierarchy", "HTTP/2 & HTTP/3 QUIC", "TLS 1.3 Handshake", "IPSec & Firewalls"],
                "tasks": [
                    {
                        "task_id": "CSE3003_M5_T1",
                        "title": "Dissect HTTP/3 Multiplexing over UDP (QUIC)",
                        "weightage": 13,
                        "question": {
                            "prompt": "What major issue in HTTP/2 over TCP does HTTP/3 over QUIC eliminate?",
                            "options": [
                                "Head-of-Line (HoL) blocking at the transport layer",
                                "DNS amplification",
                                "SSL certificate expirations",
                                "Subnet fragmentation"
                            ],
                            "correct_idx": 0,
                            "explanation": "In HTTP/2, a single lost TCP packet stalls all multiplexed streams. QUIC runs over UDP with independent stream state, eliminating transport Head-of-Line blocking."
                        }
                    }
                ]
            }
        ]
    },
    "CSE3004": {
        "course_code": "CSE3004",
        "course_title": "Cloud Computing Architecture",
        "credits": 4,
        "modules": [
            {
                "module_id": 1,
                "title": "Cloud Service Models & Virtualization Mechanisms",
                "exam_weightage": 15,
                "scope_topics": ["IaaS, PaaS, SaaS", "Type-1 vs Type-2 Hypervisors", "Containerization vs VMs", "Tenancy Models"],
                "tasks": [
                    {
                        "task_id": "CSE3004_M1_T1",
                        "title": "Compare Bare-Metal Hypervisors with Kernel-based VMs",
                        "weightage": 8,
                        "question": {
                            "prompt": "Which component manages hardware execution directly without an underlying host OS in Type-1 virtualization?",
                            "options": ["Bare-Metal Hypervisor", "Host OS Kernel Driver", "VirtualBox", "Docker Engine"],
                            "correct_idx": 0,
                            "explanation": "Type-1 hypervisors (e.g. VMware ESXi, Xen) run directly on the physical hardware without a general-purpose host OS."
                        }
                    }
                ]
            },
            {
                "module_id": 2,
                "title": "Cloud Storage & Elastic Compute Scaling",
                "exam_weightage": 15,
                "scope_topics": ["Block vs Object vs File Storage", "Auto-scaling Groups", "Load Balancing Algorithms", "Stateless Architecture"],
                "tasks": [
                    {
                        "task_id": "CSE3004_M2_T1",
                        "title": "Architect S3 Object Storage Lifecycle Rules",
                        "weightage": 8,
                        "question": {
                            "prompt": "What is a defining characteristic of Object Storage (e.g. AWS S3) compared to Block Storage?",
                            "options": [
                                "Direct mount as a bootable OS root filesystem",
                                "Flat namespace accessible via RESTful HTTP APIs with immutable object updates",
                                "Sector-by-sector disk write capabilities",
                                "Sub-millisecond random in-place byte edits"
                            ],
                            "correct_idx": 1,
                            "explanation": "Object storage organizes data into flat key-value namespaces accessed via HTTP verbs (GET, PUT) where objects are replaced immutably."
                        }
                    }
                ]
            },
            {
                "module_id": 3,
                "title": "Serverless Computing & Microservices Choreography",
                "exam_weightage": 20,
                "scope_topics": ["Event-driven Architecture", "AWS Lambda / FaaS Lifecycle", "Message Queues (SQS/Kafka)", "API Gateways"],
                "tasks": [
                    {
                        "task_id": "CSE3004_M3_T1",
                        "title": "Mitigate Serverless Cold Starts and Concurrency Limits",
                        "weightage": 10,
                        "question": {
                            "prompt": "What technique effectively maintains pre-initialized runtime execution environments for serverless functions?",
                            "options": ["Provisioned Concurrency", "Cold Swapping", "Overclocking vCPUs", "DNS Caching"],
                            "correct_idx": 0,
                            "explanation": "Provisioned Concurrency keeps a defined pool of execution environments initialized and ready to respond instantaneously."
                        }
                    }
                ]
            },
            {
                "module_id": 4,
                "title": "Cloud Security, IAM & Zero Trust Architecture",
                "exam_weightage": 25,
                "scope_topics": ["Shared Responsibility Model", "Least Privilege IAM Policies", "VPC Security Groups vs NACLs", "KMS Encryption"],
                "tasks": [
                    {
                        "task_id": "CSE3004_M4_T1",
                        "title": "Configure Stateful Security Groups vs Stateless NACLs",
                        "weightage": 12,
                        "question": {
                            "prompt": "Because VPC Security Groups are stateful, what happens when inbound traffic is allowed on port 443?",
                            "options": [
                                "Outbound return traffic is automatically allowed regardless of outbound rules",
                                "Outbound traffic must be explicitly allowed in rule table",
                                "Traffic is inspected twice by firewall",
                                "Port 80 is also opened automatically"
                            ],
                            "correct_idx": 0,
                            "explanation": "Security groups are stateful: return traffic is automatically permitted irrespective of outbound rules."
                        }
                    }
                ]
            },
            {
                "module_id": 5,
                "title": "Infrastructure as Code (IaC) & Multi-Region Reliability",
                "exam_weightage": 25,
                "scope_topics": ["Terraform State Management", "Disaster Recovery (RPO/RTO)", "Global Accelerator", "Cost Optimization"],
                "tasks": [
                    {
                        "task_id": "CSE3004_M5_T1",
                        "title": "Engineer Multi-Region Active-Active DR with Route 53",
                        "weightage": 13,
                        "question": {
                            "prompt": "What disaster recovery metric specifies the maximum acceptable data loss measured in time?",
                            "options": ["Recovery Point Objective (RPO)", "Recovery Time Objective (RTO)", "MTBF", "SLA Percentile"],
                            "correct_idx": 0,
                            "explanation": "RPO (Recovery Point Objective) measures the maximum acceptable age of data files that must be recovered from backup storage for normal operations."
                        }
                    }
                ]
            }
        ]
    },
    "CSE3005": {
        "course_code": "CSE3005",
        "course_title": "Web Technologies",
        "credits": 3,
        "modules": [
            {
                "module_id": 1,
                "title": "Modern JavaScript (ES6+), DOM & Asynchronous Programming",
                "exam_weightage": 15,
                "scope_topics": ["Event Loop & Microtasks", "Promises & async/await", "Closures & Scoping", "Fetch API"],
                "tasks": [
                    {
                        "task_id": "CSE3005_M1_T1",
                        "title": "Trace JavaScript Microtask vs Macrotask Queue Execution",
                        "weightage": 8,
                        "question": {
                            "prompt": "In the browser event loop, which queue has execution priority after the synchronous call stack empties?",
                            "options": [
                                "Microtask queue (Promise callbacks, queueMicrotask)",
                                "Macrotask queue (setTimeout, setInterval)",
                                "Rendering frame repaint pipeline",
                                "IndexedDB batch queue"
                            ],
                            "correct_idx": 0,
                            "explanation": "All microtasks in the microtask queue are drained completely before the event loop picks the next macrotask from the task queue."
                        }
                    }
                ]
            },
            {
                "module_id": 2,
                "title": "Component-based UI Engineering & State Management",
                "exam_weightage": 15,
                "scope_topics": ["Virtual DOM Reconciliation", "Hooks Lifecycle", "State Colocation", "Prop Drilling vs Context"],
                "tasks": [
                    {
                        "task_id": "CSE3005_M2_T1",
                        "title": "Optimize Component Re-renders with Memoization",
                        "weightage": 7,
                        "question": {
                            "prompt": "What is the primary function of the useMemo hook?",
                            "options": [
                                "Directly mutate DOM node attributes",
                                "Cache the computed result of an expensive calculation between re-renders",
                                "Dispatch asynchronous network calls on mount",
                                "Register global event listeners"
                            ],
                            "correct_idx": 1,
                            "explanation": "useMemo memoizes the return value of an expensive calculation until its specified dependency array changes."
                        }
                    }
                ]
            },
            {
                "module_id": 3,
                "title": "Backend API Development & Authentication",
                "exam_weightage": 20,
                "scope_topics": ["RESTful Standards", "JWT vs Session Cookies", "CORS Preflight (OPTIONS)", "Middleware Pipelines"],
                "tasks": [
                    {
                        "task_id": "CSE3005_M3_T1",
                        "title": "Secure REST APIs with HttpOnly SameSite JWT Tokens",
                        "weightage": 10,
                        "question": {
                            "prompt": "Why should session JWTs be stored in HttpOnly cookies rather than localStorage?",
                            "options": [
                                "To prevent malicious client-side JavaScript from accessing tokens via XSS attacks",
                                "To allow CSS styling of the cookie payload",
                                "To double transmission speed across HTTP/1.1",
                                "Because localStorage cannot store strings"
                            ],
                            "correct_idx": 0,
                            "explanation": "HttpOnly cookies are inaccessible to document.cookie in JavaScript, mitigating token theft in Cross-Site Scripting (XSS) exploits."
                        }
                    }
                ]
            },
            {
                "module_id": 4,
                "title": "Web Performance, Core Web Vitals & PWA",
                "exam_weightage": 25,
                "scope_topics": ["Largest Contentful Paint (LCP)", "Interaction to Next Paint (INP)", "Service Workers & Caching", "Lazy Loading"],
                "tasks": [
                    {
                        "task_id": "CSE3005_M4_T1",
                        "title": "Diagnose & Minimize Interaction to Next Paint (INP)",
                        "weightage": 12,
                        "question": {
                            "prompt": "What Core Web Vital replaced FID to measure overall page responsiveness to user interactions?",
                            "options": ["Cumulative Layout Shift (CLS)", "Interaction to Next Paint (INP)", "First Contentful Paint (FCP)", "Time to Interactive (TTI)"],
                            "correct_idx": 1,
                            "explanation": "INP (Interaction to Next Paint) measures overall interaction responsiveness by tracking user interaction latency throughout the page session."
                        }
                    }
                ]
            },
            {
                "module_id": 5,
                "title": "Web Security, OWASP Top 10 & SSR/Hydration",
                "exam_weightage": 25,
                "scope_topics": ["SQL Injection & XSS", "CSRF Protection", "Content Security Policy (CSP)", "Server-Side Rendering (SSR)"],
                "tasks": [
                    {
                        "task_id": "CSE3005_M5_T1",
                        "title": "Implement Strict Content Security Policy (CSP) Headers",
                        "weightage": 13,
                        "question": {
                            "prompt": "Which HTTP response header restricts the sources from which scripts, styles, and images can load to mitigate XSS?",
                            "options": [
                                "Content-Security-Policy",
                                "X-Frame-Options",
                                "Access-Control-Allow-Origin",
                                "Strict-Transport-Security"
                            ],
                            "correct_idx": 0,
                            "explanation": "Content-Security-Policy (CSP) allows server operators to declare authorized script sources, restricting unauthorized inline scripts and injection attacks."
                        }
                    }
                ]
            }
        ]
    }
}


def get_course_syllabus(course_code: str) -> Optional[Dict[str, Any]]:
    """Returns syllabus hierarchy for a given course code."""
    return COURSE_SYLLABUS_DB.get(course_code)


def get_all_course_codes() -> List[str]:
    """Returns all available course codes in the syllabus dictionary."""
    return list(COURSE_SYLLABUS_DB.keys())


def get_modules_for_exam(course_code: str, target_exam: str) -> List[Dict[str, Any]]:
    """
    Filters modules based on target exam:
    - Mid-1: Modules 1 & 2
    - Mid-2: Modules 3 & 4
    - FAT / Finals: Modules 1, 2, 3, 4, 5
    """
    syllabus = get_course_syllabus(course_code)
    if not syllabus:
        return []

    all_modules = syllabus["modules"]
    if target_exam == "Mid-1 (Internal Assessment 1)":
        return [m for m in all_modules if m["module_id"] in (1, 2)]
    elif target_exam == "Mid-2 (Internal Assessment 2)":
        return [m for m in all_modules if m["module_id"] in (3, 4)]
    else:  # Finals / FAT / Comprehensive
        return all_modules


def get_quiz_question_by_task_id(task_id: str) -> Optional[Dict[str, Any]]:
    """Finds and returns the active-recall question object for a given task ID."""
    for course_data in COURSE_SYLLABUS_DB.values():
        for module in course_data["modules"]:
            for task in module.get("tasks", []):
                if task["task_id"] == task_id:
                    q = task.get("question")
                    if q:
                        return {
                            "task_id": task_id,
                            "task_title": task["title"],
                            "prompt": q["prompt"],
                            "options": q["options"],
                            "correct_idx": q["correct_idx"],
                            "explanation": q["explanation"]
                        }
    return None
