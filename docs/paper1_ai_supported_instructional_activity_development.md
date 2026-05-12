# AI-Supported Instructional Activity Development for Multilingual Science Classrooms: A Two-Chatbot Workflow

## Abstract

Designing short, standards-based science activities for multilingual students requires teachers to coordinate disciplinary goals, language development, inquiry routines, culturally and linguistically responsive participation, materials, assessment, and classroom feasibility. General-purpose AI tools can make lesson generation faster, but they also risk producing generic activities that treat multilingual support, standards alignment, or creative engagement as optional add-ons. This paper examines a two-chatbot workflow developed to support 35 teachers as they moved from an initial instructional idea to a final science activity. The first tool, SciLingBot, was designed around a hybrid instructional identity grounded in the 5E instructional model, SIOP, and translanguaging. The second tool, PTBot, was designed around possibility thinking to widen modes of participation, engagement patterns, contingency planning, and teacher agency. Data sources included teachers' workflow artifacts from initial idea to final product and the final 35 teacher activities. The analysis combined process-oriented thematic analysis of the workflow with product-oriented thematic analysis of final activities, checking how the final designs reflected each tool's identity. Findings suggest that the two-bot sequence was not redundant. SciLingBot created convergence around standards, lesson structure, science-language integration, and multilingual access. PTBot then introduced divergence by inviting teachers to ask what else might be possible under real classroom constraints. In stronger cases, teachers reconverged by selecting feasible, coherent, and more engaging activity designs. The study contributes a design logic for specialized teacher-facing AI tools: AI can support teacher agency when it is organized as a structured co-design process rather than a generic lesson-completion engine.

## Introduction

Science teachers are asked to design activities that are standards-based, inquiry-oriented, accessible to multilingual learners, and feasible within limited classroom time. This is a demanding design problem. A teacher must identify the science standard, translate that standard into an age-appropriate activity, support academic language, provide comprehensible input, invite interaction, use materials students can manipulate, assess understanding, and make the work meaningful for students with different language histories and classroom experiences. For multilingual learners, the challenge is intensified when science instruction is treated as English-only content delivery rather than as participation in language-rich scientific sense-making.

Generative AI creates an important opportunity in this design space. It can help teachers produce first drafts, reorganize activities, suggest scaffolds, generate examples, and propose alternative formats. However, the same strength creates a second challenge. Generic AI tools often respond to surface-level prompts with plausible but under-theorized lesson plans. They may include objectives without meaningful assessment, mention multilingual students without designing for their participation, or add engagement features that are disconnected from standards and inquiry. For teachers working under pacing pressures, policy demands, and limited planning time, a generic activity may look complete while still failing to support multilingual science learning.

This paper begins from that tension: the opportunity of AI is real, but general-purpose AI is not enough. The design need is for custom AI tools whose identities are built from instructional theory, equity commitments, and teacher-facing workflow logic. In this study, that need was addressed through two separate chatbots. SciLingBot was designed to produce a structured instructional base aligned with standards-based science, the 5E model, SIOP, and translanguaging. PTBot was designed to reopen the design space through possibility thinking, helping teachers ask what else the activity could become, how students might engage more fully, and what obstacles should be anticipated before classroom use.

The paper's chain of logic is therefore: teachers face the challenge of designing engaging, standards-based science lessons for multilingual students; AI offers a possible support; generic AI creates a second challenge because it can produce coherent-looking but generic activities; custom AI tools are needed; SciLingBot provides alignment and structure; PTBot provides engagement, possibility, and contingency planning; teachers use a three-step workflow to move from initial idea to final product; and the final activities of 35 teachers are analyzed thematically to examine how the two chatbot identities worked together.

The central research question guiding this paper is: How did a two-chatbot workflow support teachers' development of standards-based science activities for multilingual learners, and how were the instructional identities of SciLingBot and PTBot reflected in the final activities?

The contribution to research is a model of specialized AI-supported instructional design in which chatbot identity is treated as a theoretically designed pedagogical tool rather than as a neutral interface. The contribution to practice is a replicable three-step workflow that helps teachers converge around instructional coherence, diverge toward creative and inclusive possibilities, and reconverge around feasible classroom activity designs.

## Framework: Tool Development

### Why Two Separate Chatbots?

The two-chatbot workflow was intentionally staged. SciLingBot created a structured base that teachers could work with. PTBot then shifted the design's center of gravity by broadening modes, engagement patterns, and contingency planning. The two bots were therefore not redundant. They staged convergence before divergence and, in stronger cases, divergence before reconvergence.

This design decision matters because teachers' activity development involves both coherence and imagination. A lesson that is imaginative but weakly aligned may be difficult to justify, assess, or teach. A lesson that is tightly aligned but unimaginative may fail to invite multilingual students into meaningful participation. The two-bot sequence was designed to protect both needs. SciLingBot first stabilized the lesson around standards, content and language objectives, inquiry flow, scaffolds, and multilingual participation. PTBot then pushed the teacher to consider what the activity might become if it were more embodied, visual, collaborative, culturally grounded, bilingual, public, playful, or resilient to predictable classroom constraints.

### SciLingBot as a Hybrid Instructional Identity

The SciLingBot backend is best understood as a deliberately hybrid instructional identity rather than as a generic lesson-plan prompt. It integrated three frameworks: the 5E instructional model, SIOP, and translanguaging.

The 5E model contributed the epistemic spine of the lesson. Students are oriented to a phenomenon or problem, explore it, explain what they are noticing, elaborate by applying or extending their understanding, and evaluate what they have learned. The BSCS research tradition links learning-cycle instruction with gains in science content mastery, scientific reasoning, and interest in science when implemented with coherence and fidelity (BSCS Science Learning, 2022; Bybee et al., 2006). For this project, 5E helped prevent the AI from generating activities that merely listed facts or procedures. It pushed the activity toward inquiry, sequence, and sense-making.

SIOP contributed a different but complementary architecture. Its core value is that it makes content instruction legible to multilingual learners through explicit content and language objectives, comprehensible input, background building, interaction routines, scaffolded practice, and review and assessment. In the sheltered-instruction research program summarized by Short, Echevarria, and Richards-Tutor (2011), students whose teachers implemented SIOP with fidelity performed significantly better on academic language and literacy measures than comparison students. For this project, that evidence matters because the design task was never simply to make science fun. It was to make science learnable for multilingual learners in a short classroom window.

Translanguaging added the equity stance that neither 5E nor SIOP alone fully guarantees. Translanguaging reframes students' full linguistic repertoires as resources for sense-making rather than interference to be suppressed. The WIDA/NSTA design principles for multilingual science argue that multilingual learners should be able to begin with familiar language practices and expand their repertoires through science activity (MacDonald et al., 2020). Gonzalez-Howard, Andersen, Mendez Perez, and Suarez (2023) similarly show that a translanguaging lens helps researchers and teachers notice richer scientific sense-making across multilingual and multimodal resources than English-only lenses tend to capture.

SciLingBot's identity therefore had three linked commitments. The 5E model organized the inquiry arc. SIOP made that arc teachable through objectives, interaction, differentiation, and assessment. Translanguaging positioned multilingual participation as an epistemic asset rather than a remediation problem.

### PTBot and Possibility Thinking

Possibility thinking (PT) is the cognitive and pedagogical process of transforming "what is" into "what might be." It emphasizes creativity, imagination, innovation, and agency through questions such as "What if?" and "As if?" Craft and colleagues describe possibility thinking as central to creativity in education because it supports question-posing, question-responding, and imaginative movement from existing conditions toward alternatives (Craft et al., 2013). Beghetto (2023a, 2023b) extends this logic by framing education as a site for broadening horizons of the possible, including through human-AI collaboration. Glaveanu, Karwowski, Ross, and Beghetto (2024) operationalize possibility thinking through awareness of the possible, excitement about the possible, and exploration of the possible, linking PT to creative agency. Recent teacher-focused work also suggests that PT training can strengthen educators' creative self-perceptions when it is embedded in reflective and collaborative professional learning (Mangion et al., 2025).

This matters under restriction. Teachers often design within standards, pacing guides, limited materials, short time windows, English-dominant norms, assessment demands, and professional learning systems that narrow rather than expand choice. Research on creativity from constraints is useful here because constraints can function as focusing devices when practitioners are supported in leveraging them productively (Tromp & Baer, 2022). Curriculum policy studies point in the same direction: teachers do not simply implement policy. They adopt, adapt, translate, negotiate, and sometimes strategically narrow it depending on autonomy, available artifacts, local pressures, and support (Lambert et al., 2021; Robinson, 2012). Studies of curriculum reform similarly show that agency strengthens when teachers have collaborative support and reform-literacy opportunities, and weakens when enactment becomes constrained, fragmented, or fear-based (Wang, 2022; Xie et al., 2024).

PTBot was placed after SciLingBot because possibility thinking without instructional structure can become disconnected from standards or classroom feasibility. Placed after SciLingBot, PTBot strengthened what AI could provide to teachers. SciLingBot's 5E, SIOP, and translanguaging identity gave the AI a strong backbone: inquiry sequence, language objectives, comprehensible input, interaction routines, scaffolded practice, assessment slots, and multilingual participation structures. PTBot then added a deliberately divergent phase by asking what else might be possible for the same lesson, followed by a reconvergent phase that stress-tested those ideas against likely breakdowns. In creativity terms, that sequence matters because high-quality creative work depends on both divergent generation and convergent selection (Rawlings & Cutting, 2024). In design terms, the AI is no longer only a lesson-completion engine. It becomes a structured co-designer that can preserve instructional coherence while widening modality, cultural connection, resourcefulness, and implementation readiness.

### AI, Agency, and the Risk of Generic Support

Recent scholarship raises a productive tension for teacher-facing AI design. On one hand, AI assistance may improve short-term performance while weakening memory, creativity, and critical thinking when users offload too much of the thinking process to the tool (Gerlich, 2025; Hurley, 2025; Lee et al., 2025). On the other hand, research on general-purpose systems suggests that AI can strengthen structure, logical reasoning, and problem definition while contributing less consistently to novelty, multidisciplinary integration, and the rejection of unsupported conclusions, particularly when use is passive rather than dialogic (Musazade et al., 2025). These concerns are especially relevant for instructional design, where efficiency alone is insufficient if it comes at the cost of pedagogical judgment and adaptive reasoning.

For this reason, the SciLingBot-PTBot sequence was designed not as a generic lesson-generation system but as a pair of specialized, knowledge-augmented pedagogical tools with distinct roles. SciLingBot provided a structured backbone grounded in 5E, SIOP, and translanguaging. PTBot reopened the design space through possibility thinking, alternatives, tradeoffs, and contingency planning. Framed this way, the workflow positioned AI not as a substitute for teacher thought but as a structured support for teacher agency, creative engagement, and critical pedagogical reflection.

This agency emphasis also fits recent professional-learning research. Mohammad Nezhad and Stolz (2025) describe an illusion of choice when policy, leadership, and compliance structures dominate teachers' professional development; in such settings, agency weakens because teachers are positioned as recipients rather than decision-makers. By contrast, studies of curriculum adaptation show that teachers exercise practical-evaluative and projective agency when they reinterpret official curricula for their own students (Valdelamar Gonzalez & Calle-Diaz, 2023). Banegas, Budzenski, and Yang (2024) show that projective agency for multilingual classrooms can be intentionally developed through curriculum work, including stronger willingness to use agency for professional development and critical teaching practice. Lin's (2025) translanguaging professional-development study similarly reports increased self-efficacy and motivation to enact more equitable instruction after participatory translanguaging workshops.

Teacher agency is especially important in diverse and multilingual classrooms. Translanguaging and multilingual-teacher-agency research shows that teachers often work inside monolingual or English-dominant policy environments yet still create more inclusive instruction by negotiating those norms, reducing cognitive and affective barriers, and legitimizing students' full communicative repertoires (Ou & Gu, 2024; Seki, 2025). Responsive schooling for immigrant and multilingual learners depends not only on teacher goodwill but also on professional freedom and supports that allow teachers to interpret policy in ways that actually serve students (Villavicencio et al., 2024). PTBot was therefore relevant not only to lesson quality but also to teacher agency and confidence. It gave teachers repeated practice in generating alternatives, judging tradeoffs, anticipating obstacles, and selecting a defensible direction. This interpretation is consistent with research linking creative teaching behavior to creative teaching self-efficacy (Shi et al., 2023).

## Methodology: Participant Process

### Study Context and Participants

The study examined the activity-development work of 35 teachers who used a two-chatbot workflow to design science instructional activities for multilingual students. The task was to move from an initial activity idea to a final classroom-ready product. The activities were expected to address science standards, support multilingual learners, and fit within realistic classroom constraints.

The paper treats teachers as designers rather than as users who merely accepted AI output. This distinction is important. The workflow was not analyzed as a measure of chatbot correctness alone. It was analyzed as a co-design process in which teachers interpreted, selected, revised, and finalized AI-supported suggestions.

### The Three-Step Workflow

Teachers moved through a three-step workflow.

Step 1 was the initial idea. Teachers began with a science topic, standard, phenomenon, student need, or activity concept. These initial ideas varied in specificity. Some began with a clear standard or activity structure, while others began with a general content area or classroom problem.

Step 2 was SciLingBot-supported alignment. Teachers used SciLingBot to develop the idea into a more structured activity. The bot prompted attention to standards, content objectives, language objectives, 5E sequence, SIOP-aligned scaffolds, materials, interaction, assessment, and translanguaging opportunities. This step functioned as convergence. It helped teachers stabilize the activity around the core requirements of multilingual science instruction.

Step 3 was PTBot-supported expansion and reconvergence. Teachers then used PTBot to consider alternatives, engagement patterns, multimodal participation, cultural or community connections, material constraints, likely breakdowns, and contingency plans. This step functioned first as divergence, then as reconvergence. Teachers were not expected to include every idea PTBot generated. They were expected to decide which possibilities strengthened the activity while preserving coherence and feasibility.

### Data Sources

The analysis drew on two data sources. The first was teachers' workflow artifacts from initial idea to final product. These artifacts were used to examine how the activity changed across the three-step process and how teachers used the two bots' different identities.

The second was the set of 35 final teacher activities. These final products were analyzed thematically to check alignment with each tool. The analysis asked: Where do final activities show SciLingBot's identity through standards alignment, 5E structure, SIOP features, and translanguaging supports? Where do they show PTBot's identity through possibility expansion, engagement, multimodality, cultural or linguistic responsiveness, teacher choice, and contingency planning? Where do the two identities work together?

A supplementary product-level alignment check also drew on the existing SIOP activity analysis artifacts in the project repository. That check focused on written evidence in final activity texts. It did not claim to measure classroom implementation.

### Analytic Approach

The analysis used thematic analysis at two levels. First, the workflow artifacts were examined as process data. The goal was to identify how teachers' designs changed from initial idea to final product, especially where SciLingBot appeared to create instructional coherence and where PTBot appeared to widen or refine the design.

Second, the final activities were examined as product data. Codes were organized around the two chatbot identities. SciLingBot-aligned codes included standards alignment, content objectives, language objectives, 5E inquiry sequence, comprehensible input, explicit vocabulary, interaction, scaffolding, review and assessment, and translanguaging. PTBot-aligned codes included "what if" alternatives, multimodal engagement, embodied participation, collaboration, culturally grounded connections, resource adaptation, student choice, public sharing, and contingency planning.

The analysis then looked for patterns of integration. A final activity was considered a stronger two-bot case when it preserved the instructional architecture from SciLingBot and also showed PTBot-style expansion that improved engagement, inclusion, or implementation readiness without weakening the core science and language goals. Within the product analysis, Activity 13 was selected as a representative qualitative case because it showed the strongest written SIOP alignment across the 35 activities while also providing visible evidence of 5E structure, translanguaging support, and PTBot refinement.

## Findings: Themes in Teacher Workflow and Final Activities

### Theme 1: SciLingBot Turned Initial Ideas Into Instructional Architecture

Across the workflow, SciLingBot's strongest role was to turn initial ideas into teachable instructional architecture. Initial ideas often named a science topic or activity, but SciLingBot helped make the activity more instructionally complete. The final products more consistently included content objectives, language objectives, materials, interaction structures, and assessment opportunities. This pattern reflects the bot's SIOP identity: it did not treat language support as a side note but as part of the lesson structure.

SciLingBot also helped place activities inside an inquiry arc. Instead of moving directly from teacher explanation to student product, many final activities asked students to observe, manipulate, discuss, compare, explain, test, or reflect. This pattern reflects the 5E identity. In stronger activities, students were not simply told science vocabulary. They encountered a phenomenon or problem, explored it through materials or data, explained what they noticed, applied ideas in a new task, and showed understanding through a product, discussion, or quick assessment.

The product-level analysis supports this interpretation. The strongest written traces across the final activity set were associated with supplementary materials, comprehensible input, meaningful integration of science concepts and language practice, scaffolded instruction, interaction, hands-on materials, and integration of multiple language skills. These are precisely the areas SciLingBot was designed to foreground.

### Theme 2: SciLingBot Positioned Multilingual Support as Part of Science Learning

SciLingBot also shifted multilingual support from accommodation to participation. In many final activities, multilingual learners were supported through visuals, real objects, gestures, sentence frames, bilingual labels, partner talk, group roles, drawing, labeling, oral rehearsal, and opportunities to use home language before sharing in English. These supports matter because they make science concepts available through multiple semiotic and linguistic pathways.

The strongest activities treated translanguaging as a bridge into scientific sense-making. Students could discuss observations in a familiar language, compare terms across languages, label drawings in English and/or home language, or use multilingual resources to clarify concepts. This aligns with translanguaging scholarship that treats students' full repertoires as resources for learning rather than as barriers to English academic language development (Gonzalez-Howard et al., 2023; MacDonald et al., 2020).

However, the final activities also showed unevenness. Translanguaging was often present as discussion support, bilingual vocabulary, or home-language bridging, but less often developed into full multilingual assessment, family/community language resources, or systematic analysis of bilingual student products. This distinction is important. The two-bot workflow helped teachers make translanguaging visible, but future iterations should push more explicitly toward multilingual products, multilingual evidence of learning, and assessment practices that value bilingual sense-making as evidence rather than as a pre-English step.

### Theme 3: PTBot Reopened the Design Space After Alignment

PTBot's strongest role was to reopen the design space after SciLingBot had created a coherent base. Once the activity had standards, objectives, sequence, and scaffolds, PTBot prompted teachers to ask what else might be possible. This shift was visible in final activities that included more varied participation modes, more student choice, more embodied or visual engagement, more collaborative formats, and more attention to classroom constraints.

In the workflow logic, PTBot did not replace SciLingBot's structure. It worked on top of it. This sequencing helped avoid two common problems: generic creativity that is disconnected from the science objective, and rigid alignment that produces technically correct but low-engagement activities. PTBot pushed the teacher to consider alternatives while still returning to feasibility. This is the divergence-reconvergence movement at the center of possibility thinking.

Examples of PTBot-aligned movement included reframing a demonstration as a student investigation, adding a gallery walk or group role structure, inviting students to represent ideas through drawings or models, connecting the phenomenon to students' homes or communities, offering low-material alternatives, and anticipating problems such as limited time, missing materials, uneven language proficiency, or student confusion. These features show PTBot's engagement and contingency identity.

### Theme 4: Strong Final Activities Integrated the Two Identities Rather Than Alternating Between Them

The strongest final activities did not read as two separate layers, one aligned and one creative. Instead, they integrated the two identities. In these activities, the standards-based science goal remained visible, the 5E sequence organized the activity, language objectives were connected to student discourse, translanguaging supported sense-making, and possibility-thinking moves made the activity more engaging or resilient.

This pattern can be described as convergence, divergence, and reconvergence. SciLingBot first converged the design around instructional coherence. PTBot then diverged by proposing alternative modes, materials, and engagement patterns. Teachers then reconverged by selecting the options that best fit their students, classroom time, and resources.

The representative SIOP case analysis in the project illustrates this integration. Activity 13, a kindergarten physical science lesson on comparing pushes and pulls, was selected because it was the strongest SIOP case in the corpus: it received a SIOP total of 112 out of 120, a SIOP average of 3.73 out of 4, 29 of 30 SIOP features scored as clearly or highly evident, all eight SIOP components met the high-alignment threshold, and the activity also showed a complete 5E sequence. Its translanguaging score was more moderate, 2.40 out of 4, which makes it useful as a representative case precisely because it shows both the strength and the limits of the final products.

Activity 13 also shows why the workflow should be interpreted as iterative co-design rather than one-step AI generation. The teacher's initial idea already contained a sound instructional seed: a kindergarten physical science activity in which students would compare pushes and pulls, work in groups with machines or objects, discuss differences, use sentence frames, receive peer language modeling from mixed English-proficiency partners, and complete informal assessment. The initial idea included a measurable objective, but it was less developed in sequence, differentiation, explicit multilingual support, standards alignment, and assessment detail. SciLingBot did not create the lesson from nothing. It expanded the teacher's idea into a more complete instructional architecture.

In the SciLingBot version, the activity included both a content objective and a language objective. Students were expected to describe different pushes and pulls using classroom objects or simple machines, and to use sentence frames to compare and describe those actions in oral discussion. The activity then organized students into a short hands-on sequence: students explored familiar objects in mixed-proficiency groups, discussed and charted which objects were pushed, pulled, or both, and completed a quick formative reflection using examples, picture cards, or thumbs-up/thumbs-down checks. This illustrates SciLingBot's core contribution. Content objectives, language objectives, materials, hands-on investigation, scaffolds, interaction, review, assessment, and standards alignment were brought into one coherent lesson sequence rather than appearing as disconnected checklist items.

The activity's 5E alignment was visible in student actions, not only in labels. Students engaged with familiar classroom objects, explored pushes and pulls through manipulation, explained findings through discussion and charting, elaborated through a problem-solving extension, and evaluated understanding through quick checks and teacher notes. Its SIOP alignment was similarly concrete. The lesson preparation included paired content and language goals; comprehensible input was supported through real objects, visuals, gestures, charting, modeling, and sentence frames; interaction was supported through mixed-proficiency groups and whole-class discussion; practice and application were embedded in manipulation, observation, drawing, labeling, and oral explanation; and review and assessment were built into the lesson rather than postponed to the end.

The translanguaging evidence in Activity 13 was explicit but less saturated than the SIOP and 5E evidence. The activity allowed students to discuss findings in their home language before sharing in English, invited students to share how "push" and "pull" are said in their home languages, used bilingual labels or picture cards, and allowed students to draw or label observations in English and/or home language. These moves positioned home language as a bridge into science discourse. At the same time, the written activity provided less evidence of flexible multilingual assessment, systematic assessment of bilingual products, or family/community language resources in the SciLingBot version. Thus, Activity 13 should be read as a strong SIOP and 5E case with moderate translanguaging integration, not as the strongest possible translanguaging case.

The PTBot refinement strengthened the activity without abandoning its core design. It kept the same science focus and standards, but made the lesson more concrete, playful, and responsive. The refined version added pre-lesson family participation through a bilingual note asking students to bring or draw a home object that pushes, pulls, or does both. It expanded hands-on exploration into rotating stations, added a "both" category to address likely conceptual confusion, assigned roles such as Reporter, Demonstrator, and Vocabulary Helper, expanded sentence frames, and replaced or supplemented the original extension with a schoolwide Force Walk. During the Force Walk, students would observe pushes, pulls, and "both" actions in locations such as the playground, hallway, and lunchroom, then compare patterns back in class.

This refinement shows PTBot's distinctive contribution. The bot did not simply decorate the lesson with engagement. It widened the design in ways that strengthened conceptual clarity, participation equity, home-school connection, multimodal representation, and implementation readiness. The "both" category anticipated a likely science misconception. Rotating stations made the Explore phase more varied and concrete. Student roles reduced participation imbalance. The home-object task connected household experience to classroom science and strengthened translanguaging and culturally responsive participation. The Force Walk broadened the Elaborate phase by asking students to compare forces across school contexts rather than only solve a classroom movement problem.

Activity 13 therefore makes the paper's central finding visible in one case. The teacher began with a compact but promising activity idea. SciLingBot converged the idea into a standards-aligned, SIOP-structured, 5E-organized, multilingual science lesson. PTBot then diverged toward new possibilities and reconverged around feasible refinements. The final design was stronger because the two chatbot identities worked together: SciLingBot protected instructional coherence, while PTBot expanded engagement, contingency planning, and teacher agency.

### Theme 5: The Workflow Supported Teacher Agency by Making Design Decisions Visible

The two-bot workflow supported teacher agency because it made design decisions visible. Teachers were not simply receiving a finished lesson. They were moving through a sequence that required them to clarify goals, examine supports, consider alternatives, anticipate obstacles, and choose among options. This matters because agency is not only freedom from constraint. It is the ability to act with judgment inside constraint.

SciLingBot supported practical-evaluative agency by helping teachers translate standards and multilingual learner needs into a feasible lesson structure. PTBot supported projective agency by helping teachers imagine alternative futures for the activity: more embodied, more collaborative, more bilingual, more culturally grounded, more public, or more resourceful. Together, the bots supported a form of teacher agency that was both disciplined and imaginative.

This finding is important in light of research on professional learning and policy enactment. Teachers' agency weakens when professional tools position them as recipients of compliance-oriented materials (Mohammad Nezhad & Stolz, 2025). It strengthens when curriculum work gives teachers tools for interpretation, adaptation, and future-oriented decision-making (Banegas et al., 2024; Valdelamar Gonzalez & Calle-Diaz, 2023). The two-bot workflow functioned as that kind of tool. It did not remove constraints, but it helped teachers work more deliberately within them.

### Theme 6: Final Activities Still Under-Documented Some Classroom-Dependent Practices

The final activities also revealed limitations. Some important practices were under-documented in written products, especially wait time, responsive feedback, explicit vocabulary review, comprehensive review of content concepts, and flexible multilingual assessment. These absences should be interpreted carefully. A written activity that does not mention wait time does not prove that a teacher would not provide it. A written activity that does not document feedback does not prove feedback would be absent in implementation. It means only that the final artifact did not make those practices explicit.

This finding points to an important design implication for future chatbot development. Specialized AI tools should prompt teachers not only to include visible activity components but also to document facilitation practices that often remain tacit. Future versions of SciLingBot and PTBot should therefore ask teachers to specify wait time, feedback moves, multilingual assessment options, review routines, and what the teacher will do if student responses reveal confusion.

## Discussion: Contributions and Limitations

### Contributions to AI-Supported Instructional Design

This study contributes to research on AI-supported instructional design by showing why chatbot identity matters. The relevant design question is not only whether AI can produce lesson plans. It is what kind of pedagogical identity is built into the AI, how that identity structures the teacher's workflow, and how the teacher is positioned in relation to the tool.

SciLingBot and PTBot demonstrate one possible answer. SciLingBot was designed as a convergence tool. It helped teachers align their activities with standards, 5E, SIOP, and translanguaging. PTBot was designed as a divergence and reconvergence tool. It helped teachers broaden the activity, consider engagement, anticipate obstacles, and select feasible alternatives. Together, they formed a workflow that supported structure without reducing teacher judgment and supported creativity without abandoning instructional coherence.

This design logic responds directly to concerns about passive AI use. If teachers simply ask a generic chatbot to "make a lesson," the tool can encourage cognitive offloading and reduce critical engagement. If the workflow requires teachers to move through structured alignment, possibility generation, tradeoff analysis, and final selection, AI use can instead become a form of supported pedagogical reasoning.

### Contributions to Multilingual Science Education

The paper also contributes to multilingual science education by connecting standards-based science activity design with translanguaging and teacher agency. Multilingual support was not treated as a translation feature or a final accommodation. It was embedded in the activity architecture: objectives, materials, interaction, representation, discussion, and assessment.

At the same time, the analysis shows that translanguaging integration requires continued attention. Many activities supported home-language discussion or bilingual vocabulary, but fewer fully valued multilingual products or multilingual assessment as evidence of science learning. This suggests that custom AI tools can help teachers begin to include translanguaging, but stronger tool prompts and professional learning are needed to deepen the move from linguistic access to epistemic justice.

### Contributions to Practice

For practice, the study offers a concrete workflow. Teachers and teacher educators can separate AI-supported activity development into three moves: begin with the teacher's own initial idea; use a specialized alignment bot to create a coherent standards-based multilingual science activity; then use a possibility-thinking bot to expand, stress-test, and refine the activity before finalizing it.

This workflow is useful because it resists both generic AI output and overly rigid planning templates. It gives teachers a structured way to preserve standards and language support while still widening the activity's possibilities. In professional development, the workflow can also make teacher reasoning visible. Facilitators can ask teachers to explain what they kept, what they rejected, what they adapted, and why.

### Limitations

Several limitations should guide interpretation. First, the analysis focused primarily on workflow artifacts and final written activities. Written activities can show planned supports, but they cannot prove classroom enactment. Future research should include classroom observation, teacher interviews after implementation, student artifacts, and student learning outcomes.

Second, the sample included 35 teachers, which is appropriate for qualitative thematic analysis but not sufficient for broad generalization across grade levels, schools, and policy contexts. Future studies should examine how the workflow functions with teachers who differ in science teaching experience, multilingual education preparation, AI familiarity, and access to classroom resources.

Third, the analysis of final products can identify evidence of SciLingBot and PTBot identities, but it cannot fully isolate the contribution of each bot from teachers' prior knowledge, peer discussion, instructor support, or other professional learning experiences. The workflow should therefore be understood as a co-design ecology rather than as a simple causal sequence.

Fourth, the two-bot design still depends on prompt quality, backend knowledge, and teacher uptake. A custom bot can foreground strong frameworks, but teachers still need opportunities to critique, revise, and adapt AI output. Tool development should be paired with professional learning that strengthens teachers' AI literacy, multilingual pedagogy, and creative pedagogical judgment.

## Conclusion

The problem addressed in this paper is not simply that teachers need faster lesson plans. The problem is that teachers need support designing coherent, engaging, standards-based science activities for multilingual learners under real constraints. Generic AI can help with speed, but speed alone is not the central need. The central need is structured pedagogical co-design.

The SciLingBot-PTBot workflow offers one approach. SciLingBot created convergence around standards, 5E inquiry, SIOP scaffolding, and translanguaging. PTBot created divergence around possibility, engagement, modality, cultural and linguistic connection, and contingency planning. Teachers then reconverged by selecting final designs that were more coherent, inclusive, and feasible than their initial ideas alone.

The larger implication is that teacher-facing AI should be designed around pedagogical identity and workflow, not only around output generation. When AI tools are specialized, sequenced, and used dialogically, they can support teacher agency rather than replace it. For multilingual science classrooms, that distinction matters. The goal is not to automate teacher judgment but to strengthen teachers' capacity to imagine and enact better possibilities for their students.

## References

Banegas, D. L., Budzenski, M., & Yang, F. (2024). Enhancing pre-service teachers' projective agency for diverse and multilingual classrooms through a course on curriculum development. *International Multilingual Research Journal, 18*(3), 274-289. https://doi.org/10.1080/19313152.2024.2318967

Beghetto, R. A. (2023a). A new horizon for possibility thinking: A conceptual case study of human x AI collaboration. *Possibility Studies & Society, 1*(3), 324-341. https://doi.org/10.1177/27538699231160136

Beghetto, R. A. (2023b). Broadening horizons of the possible in education. *Possibility Studies & Society, 1*(4), 414-426. https://doi.org/10.1177/27538699231182014

BSCS Science Learning. (2022). *The BSCS 5E instructional model: Origins and effectiveness*. https://bscs.org/reports/the-bscs-5e-instructional-model-origins-and-effectiveness/

Bybee, R. W., Taylor, J. A., Gardner, A., Van Scotter, P., Powell, J. C., Westbrook, A., & Landes, N. (2006). *The BSCS 5E instructional model: Origins, effectiveness, and applications*. BSCS.

Craft, A., Cremin, T., Burnard, P., Dragovic, T., & Chappell, K. (2013). Possibility thinking: Culminative studies of an evidence-based concept driving creativity? *Education 3-13, 41*(5), 538-556. https://doi.org/10.1080/03004279.2012.656671

Gerlich, M. (2025). AI tools in society: Impacts on cognitive offloading and the future of critical thinking. *Societies, 15*(1), 6. https://doi.org/10.3390/soc15010006

Glaveanu, V. P., Karwowski, M., Ross, W., & Beghetto, R. A. (2024). Possibility Thinking Scale: An initial psychometric exploration. *Possibility Studies & Society, 2*(1), 125-147. https://doi.org/10.1177/27538699241241827

Gonzalez-Howard, M., Andersen, S., Mendez Perez, K., & Suarez, E. (2023). Language views for scientific sensemaking matter: A synthesis of research on multilingual students' experiences with science practices through a translanguaging lens. *Educational Researcher, 52*(9), 525-537. https://doi.org/10.3102/0013189X231206172

Hurley, K. (2025, December 15). The paradox of AI assistance: Better results, worse thinking. *EDUCAUSE Review*. https://er.educause.edu/articles/2025/12/the-paradox-of-ai-assistance-better-results-worse-thinking

Lambert, K., Alfrey, L., O'Connor, J., & Penney, D. (2021). Artefacts and influence in curriculum policy enactment: Processes, products and policy work in curriculum reform. *European Physical Education Review, 27*(2), 258-277. https://doi.org/10.1177/1356336X20941224

Lee, H.-P., Sarkar, A., Tankelevitch, L., Drosos, I., Rintel, S., Banks, R., & Wilson, N. (2025). The impact of generative AI on critical thinking: Self-reported reductions in cognitive effort and confidence effects from a survey of knowledge workers. In *Proceedings of the 2025 CHI Conference on Human Factors in Computing Systems*. https://doi.org/10.1145/3706598.3713778

Lin, Z. (2025). Inspiring equity and pedagogical engagement with translanguaging workshops as professional development for student teachers: A participatory action research. *International Journal of Educational Research, 134*, 102778. https://doi.org/10.1016/j.ijer.2025.102778

MacDonald, R., Crowther, D., Braaten, M., Binder, W., Chien, J., Dassler, T., Shelton, T., & Wilfrid, J. (2020). *Design principles for engaging multilingual learners in three-dimensional science*. WIDA and National Science Teaching Association. https://wida.wisc.edu/resources/design-principles-engaging-multilingual-learners-three-dimensional-science

Mangion, M., Valquaresma, A., & Glaveanu, V. P. (2025). Exploring the impact of possibility thinking training on educators' creative self-perceptions: A mixed methods action research study in Maltese schools. *Methods in Psychology, 13*, 100198. https://doi.org/10.1016/j.metip.2025.100198

Mohammad Nezhad, P., & Stolz, S. A. (2025). Unveiling teachers' professional agency and decision-making in professional learning: The illusion of choice. *Professional Development in Education, 51*(6), 1067-1087. https://doi.org/10.1080/19415257.2024.2349058

Musazade, N., Mezei, J., & Wang, X. (2025). Exploring the impact of AI tools on cognitive skills: A comparative analysis. *Algorithms, 18*(10), 631. https://doi.org/10.3390/a18100631

Ou, A. W., & Gu, M. M. (2024). Teacher professional identities and their impacts on translanguaging pedagogies in a STEM EMI classroom context in China: A nexus analysis. *Language and Education, 38*(1), 42-64. https://doi.org/10.1080/09500782.2023.2244915

Rawlings, B. S., & Cutting, S. J. (2024). Linking disparate strands: A critical review of the relationship between creativity and education. *Educational Psychology Review, 36*, 135. https://doi.org/10.1007/s10648-024-09973-z

Robinson, S. (2012). Constructing teacher agency in response to the constraints of education policy: Adoption and adaptation. *The Curriculum Journal, 23*(2), 231-245. https://doi.org/10.1080/09585176.2012.678702

Seki, K. (2025). Negotiating monolingual norms: Teacher agency and translanguaging pedagogy in an English-immersion school in Japan. *The Language Learning Journal*. https://doi.org/10.1080/09571736.2025.2581070

Shi, L., Chen, S., & Zhou, Y. (2023). The influence of social capital on primary school teachers' creative teaching behavior: Mediating effects of knowledge sharing and creative teaching self-efficacy. *Thinking Skills and Creativity, 47*, 101226. https://doi.org/10.1016/j.tsc.2022.101226

Short, D. J., Echevarria, J., & Richards-Tutor, C. (2011). Research on academic literacy development in sheltered instruction classrooms. *Language Teaching Research, 15*(3), 363-380. https://doi.org/10.1177/1362168811401155

Tromp, C., & Baer, J. (2022). Creativity from constraints: Theory and applications to education. *Thinking Skills and Creativity, 46*, 101184. https://doi.org/10.1016/j.tsc.2022.101184

Valdelamar Gonzalez, C., & Calle-Diaz, L. (2023). Teachers' agency development when adapting the Colombian English suggested curriculum for high school. *PROFILE: Issues in Teachers' Professional Development, 25*(2), 201-216. https://doi.org/10.15446/profile.v25n2.104627

Villavicencio, A., Klevan, S., Patton Miranda, C., Jaffe-Walter, R., & Cherng, H. S. (2024). "The freedom to teach": The role of (re)professionalization in cultivating responsive schooling for immigrant students. *Educational Studies, 60*(2), 156-176. https://doi.org/10.1080/00131946.2024.2315981

Wang, L. (2022). English language teacher agency in response to curriculum reform in China: An ecological approach. *Frontiers in Psychology, 13*, 935038. https://doi.org/10.3389/fpsyg.2022.935038

Xie, Y., Davies, M., & Smith, J. (2024). Enacting fairly or fearfully? Unpacking the enactment of critical thinking policies in Chinese senior high schools. *Education Sciences, 14*(11), 1157. https://doi.org/10.3390/educsci14111157
