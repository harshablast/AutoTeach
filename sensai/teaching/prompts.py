from langchain import PromptTemplate

teaching_start_prompt_str = """We need to teach for the Subject: "{subject}" and the Topic: "{topic}" and the Learning Outcome: "{learning_outcome}".

We need to make sure the teaching is completely concept-based. Here is some reference material about concept-based learning:

----------
What is planning for concept-based teaching and learning?
Planning for concept-based teaching and learning is designed around transferable conceptual understandings, providing an effective way to develop students’ critical, creative, and reflective thinking. Conceptual understandings are drawn from a unit’s knowledge and/or skill learning named in a school’s learning goals, such as state or national standards. Articulating conceptual understandings in the planning process allows educators to craft factual, conceptual, and provocative questions that students encounter during learning experiences. These questions enable educators to sequence learning, moving student thinking from the factual to the conceptual level. In the process, students develop and express conceptual understandings—significant “big ideas” which transfer to new contexts. This allows students to make connections to novel situations using their prior learning and make sense of the unknown. These skills are critical for navigating current and future challenges at the local and global level. Concept-based teaching and learning builds student agency, in that learning activities ask students to construct their own ideas and support them with reasoned evidence.

What are the components of planning for concept-based teaching and learning?
Concept-based planning includes the following components:

1. Conceptual Understandings
Conceptual understandings are statements that connect two or more concepts and name the relationship between them. So that they transfer to new contexts, conceptual understandings are written in third person and present tense. They contain no proper nouns that would lock the understanding in time, place, or situation. They can follow the phrase, “Learners will understand that…” For example, “Learners will understand that…ecosystems require a balance of producers, consumers, and decomposers to function.”

In each of these instances, two or more concepts are linked together in a statement of relationship. For instance, “Artists often use their personal experiences as inspiration.” connects the concepts of artist, personal experiences, and inspiration. “Scientists engage in a process to test their hypotheses” links the concepts of scientist, process, and hypothesis. The concepts in these understandings are underlined.

In other school contexts, conceptual understandings may also be known as essential understandings, enduring understandings, central ideas (in the International Baccalaureate Programme’s Primary Years Programme), and statements of inquiry (in the International Baccalaureate Programme’s Middle Years Programme). Within a concept-based planner, educators articulate the conceptual understandings they expect students to develop as the result of specific knowledge and/or skill learning. Educators work backward from these understandings to ensure that student learning experiences support learners in moving from/between the factual to conceptual levels of thinking. In these learning experiences, students share their own understandings by reflecting on and answering conceptual questions. It would be expected that students develop multiple understandings within a unit of learning.

2. Conceptual Questions
Conceptual questions are questions that help students reach the planner’s articulated conceptual understandings through inquiry. They:

are written in the third person and present tense to ensure answers transfer to new situations.
include two or more concepts found in a conceptual understanding.
Generally, for each conceptual understanding, there are 2-3 conceptual questions that educators use to frame student learning toward the understanding. For example, for the understanding, “Ecosystems require a balance of producers, consumers, and decomposers to function,” educators may craft the conceptual questions, “How might different types of organisms live together within an ecosystem?” and “Why might ecosystems require a balance of producers, consumers, and decomposers to function?”

Conceptual questions are supported by factual and provocative questions. Factual questions name the illustrative knowledge or skills being acquired by students. For instance, in the ecosystems example, educators may ask, “What organisms live in the tropical rainforest? How do they interact and live together?” By exploring factual questions, students develop the core knowledge and skills required to answer conceptual questions and form their own understandings. Provocative questions are open-ended, supporting discussion and debate. In a unit of learning, educators generally craft 1-2 provocative questions. For example, “What is the most important organism in an ecosystem? Why?” in an ecosystems unit.

3. Concept-Based Assessment
During planning, educators create assessment tasks that ask students to demonstrate their knowledge, skills, and understanding. In a unit of learning, knowledge and skills might be assessed through activities such as quizzes or performance tasks. Assessing conceptual understanding requires educators to elicit evidence of how students:

Have formed individual concepts. Educators look at what students understand to be the characteristics of a concept and if they can name examples and non-examples of it. For instance, an example of an ecosystem would be the tundra, whereas a non-example would be a fish tank.
Make connections across concepts. Educators gather evidence about how students link concepts to form their own conceptual understandings. Educators may design tasks to do this by asking students to respond to the unit’s conceptual questions.
Transfer their understandings to new situations and contexts. For instance, once students form an understanding after learning about the tropical rainforest ecosystem, they may be asked to apply their thinking to the coral reef ecosystem.
----------

Here are the directly relevant concepts and their respective features.
{concepts}

Please teach in a conversational manner. Here are some guidelines to follow:
- Remember we want to teach with respect to the learning outcome: {learning_outcome}
- Please teach one step at a time, proceed once you recieve the user's answer, which will either be Understood or Not Understood.
- Adapt the teaching with respect to the user's understanding. Wes4 want to capture as much information about the user's conceptual understanding, so optimize for that.
- Try to ask basic questions to assess the user's understanding of the concepts in the middle of the teaching.
- Please try to include code snippets or syntax-based questions. Annotate any code snippets you want to create with ```
- Once you feel the teaching has been concluded for this learning outcome, output [END]"""
