from langchain import PromptTemplate

system_prompt = """Here are some unique qualities about you:

- You are an expert in the field of education, especially computer science education, and have decades of experience.
- You strive to drive innovation in the field of education because of the impact it can have.
- You have deep knowledge and insight in the field of educational psychology, neuroscience, and generally, how the brain learns by organizing information in a structured way.
- You have deep knowledge and expertise in computer science.
- You have a very high attention to detail and can spot the tiniest discrepancies in large amounts of information.
- You never give up and always strive to give the best efforts possible.
- You believe in the power of iteration and know that it is important to start somewhere and continuously refine from that point to achieve perfection."""

concept_hierarchy_starter_prompt_str = """We have to create an exhaustive and well structured concept hierarchy for the subject: "{subject}" and the topic: "{topic}".

Here is some information about how concepts are structured.

- Each concept is defined by certain "Features".
- Any entity which has all of these features can be considered as a "member" of this concept.
- Each concept has several "sub-concepts" within it.
- Each sub-concept within a certain concept has all the features of the concept as well as a "few more" features which differentiate each sub-concept from the other sub-concepts within the same concept.
- As we go from a concept to a sub-concept, the following will happen:
    - A concept has more "distinctiveness among members" compared to a sub-concept, but has lesser "information".
    - Eg: Animals -> Dogs, Cats, etc. Dogs -> Labradors, Pugs, etc. Animals has lesser information than Dogs/Cats and Dogs has lesser information than Labradors/Pugs. But Animals has more distinctiveness among it's members than Dogs and Dogs has more distinctiveness among it's members than Labradors.
    - As we go deeper into sub-concepts from a high level concept, we are increasing the information stored in each concept (Since the number of features are increasing by adding a "few more" at each level) and at the same time decreasing the distinctiveness among the members of each concept.


We need to create the concept hierarchy according to this paradigm of understanding concept structure. Here are some guidelines to follow while creating this:

1. We need a very exhaustive and granular hierarchy capturing all the concepts within the given topic.
2. Start from the high-level concept which is the name of the topic, and then break it down further and further. Think of how we can add a "few more" features to create a new family of sub-concepts.
3. When creating a new family of sub-concepts, remember to create the features of each sub-concept which "differentiate" it from the other sub-concepts.
4. Here, each "Feature" of each concept will be an objective propositional statement which will always be True. We can think of these as statements which the learners need to consider as True for them to understand the concept.
5. There is no limit to the number of features a concept can have.
6. While creating concepts, assign a alphanumeric IDs (Eg: TD1, G4, OSS3.9, etc) to each of them so you can refer to the ID while linking sub-concepts to their respective common concept.
7. Do keep splitting concepts into more granular sub-concepts which contain MORE INFORMATION while having LESSER DISTINCTION among their members.
8. Here is the format for reference while creating the concept hierarchy:
```
Concept ID:
Concept Name:
Common Concept: (Common Concept ID)
Distinctive Features: (List of propositional statements in bullet points)
```
9. Since this is a computer science subject, do include features which include information related to the syntax for each concept as well. This will be very important.


The subject is "{subject}" and the topic we are focusing on currently is "{topic}". Start from the high level concept "{topic}" and continue from there. Remember to think about the features of each concept and how a "few more" would result in a new family of sub concepts."""

concept_hierarchy_refine_prompt = """Let's continue breaking this down into a more granular hierarchy of concepts.

- Correct any mistakes you might have made whatsoever, this can be the concept hierarchy as a whole, certain features or links. Don't be afraid to change the whole thing if you have to!
- Focus on each concept at a time and really think if it contains all the features required to represent it. If a concept is starting to contain too many features, do not hesitate to split it up into more granular sub-concepts.
- Do remember to include features related to syntax.
- Keep breaking down concepts further till we get very granular low level concepts which are much more information dense
- Output the entire concept hierarchy from the start, this is important for consistency."""


concept_hierarchy_refine_content_prompt_str = """Here is some reference educational material related to the subject: "{subject}" and the topic: "{topic}"
{content}
----------


Here is the generated concept hierarchy so far:
{concept_hierarchy}
----------


Let's continue developing the concept hierarchy you have created so far. Follow all the guidelines mentioned above and these additional guidelines:

- Correct any mistakes you might have made whatsoever, this can be the concept hierarchy as a whole, certain features or links. Don't be afraid to change the whole thing if you have to!
- These are the things you should focus on while refining the concept hierarchy:
    - Think about each concept you have created and whether it contains all the required features to represent it fully.
    - Think about each concept and the sub-concepts which fall under it. Does each sub-concept share the features of the concept? Does each sub-concept have features which differentiate it from the other sub-concepts?
    - Think about the generated hierarchy as a whole and how to split it further.
- Feel free to take relevant features from the provided educational material, remember to focus on the parts of the content related to the topic: "{topic}".
- Do remember to include features related to syntax.
- Keep breaking down concepts further till we get very granular low level concepts which are much more information dense and specific.
- PLEASE OUTPUT THE ENTIRE CONCEPT HIERARCHY FROM THE START, this is important for consistency."""

concept_hierarchy_parse_prompt_str = """{concept_hierarchy}

Parse this into a JSON List Format as follows:
[{{
    "concept_id": STR,
    "concept_name": STR,
    "common_concept: STR, // Only the ID of the common concept
    "distinctive_features": LIST[STR]
}},
...
]"""

topic_summary_prompt_str = (
    'Provide a summary of the topic "{topic}" in the subject "{subject}":'
)

blooms_levels_descs = {
    "remember": """Remember
- Retrieving, recognizing, and recalling relevant knowledge/facts from long-term memory
- Action Verbs: list, recite, outline, define, name, match, quote, recall, identify, label, recognize"""
}

learning_outcomes_prompt_str = """The following is a Concept Hierarchy for the subject "{subject}" and the topic "{topic}"

{concept_hierarchy}

We need to create an exhaustive list of effective Learning Outcomes for the given topic "{topic}". Here are some guidelines on how to create Learning Outcomes:
- Learning Outcomes are measurable statements that articulate at the beginning what students should know, be able to do, or value as a result of taking a course or completing a program (also called Backwards Course Design)
- Learning Outcomes take the form: (action verb) (learning statement)
- Learning Outcomes should be specific, measurable, aligned with the subject, realistic and achievable.
- Avoid verbs that are unclear and cannot be observed and measured easily, for example: appreciate, become aware of, become familiar with, know, learn, and understand.
- The Learning Outcomes should exhaustively cover the given topic

We need to create the learning outcomes for the "Apply" level of Bloom's Taxonomy. Here is some more information about this:
Definition: use information or a skill in a new situation (e.g., use Newton's second law to solve a problem for which it is appropriate, carry out a multivariate statistical analysis using a data set not previously encountered).
Appropriate learning outcome verbs for this level include: apply, calculate, carry out, classify, complete, compute, demonstrate, dramatize, employ, examine, execute, experiment, generalize, illustrate, implement, infer, interpret, manipulate, modify, operate, organize, outline, predict, solve, transfer, translate, and use.

Please create an exhaustive list of Learning Outcomes for the "Apply" level of Bloom's Taxonomy. Also list the concept_ids of the concept utilized for each learning outcome."""

learning_outcomes_stages_prompt_str = """The following is a Concept Hierarchy for the subject "{subject}" and the topic "{topic}"

{concept_hierarchy}

We need to create an exhaustive list of effective Learning Outcomes for the given topic "{topic}". Here are some guidelines on how to create Learning Outcomes:
- Learning Outcomes are measurable statements that articulate at the beginning what students should know, be able to do, or value as a result of taking a course or completing a program (also called Backwards Course Design)
- Learning Outcomes take the form: (action verb) (learning statement)
- Learning Outcomes should be specific, measurable, aligned with the subject, realistic and achievable.
- Avoid verbs that are unclear and cannot be observed and measured easily, for example: appreciate, become aware of, become familiar with, know, learn, and understand.
- The Learning Outcomes should exhaustively cover the given topic

We need to create the learning outcomes for the "Apply" level of Bloom's Taxonomy. Here is some more information about this:
Definition: use information or a skill in a new situation (e.g., use Newton's second law to solve a problem for which it is appropriate, carry out a multivariate statistical analysis using a data set not previously encountered).
Appropriate learning outcome verbs for this level include: apply, calculate, carry out, classify, complete, compute, demonstrate, dramatize, employ, examine, execute, experiment, generalize, illustrate, implement, infer, interpret, manipulate, modify, operate, organize, outline, predict, solve, transfer, translate, and use.

Please create an exhaustive list of Learning Outcomes for the "Apply" level of Bloom's Taxonomy. Here are some guidelines to follow while creating these:
- Mention which concept IDs are utilized for each learning outcome.
- Organize the Learning Outcomes in a sequence of stages:
    - Group Learning Outcomes which should ideally be learned together in a stage
    - Order the stages sequentially such that we create an optimal learning path through the learning outcomes.
    - The fundamental rule of ordering is that we need to learn new information based on information we have already learnt and understood."""

learning_outcomes_parse_prompt_str = """{learning_outcomes}

Parse this into a JSON List Format as follows:
[{{
    "learning_outcome": STR,
    "concept_ids": LIST[STR]
}},
...
]"""

learing_outcomes_stages_parse_prompt_str = """{learning_outcomes_stages}

Parse this into a JSON List Format as follows:
[{{
    "learning_outcome_stage": STR,
    "learning_outcomes": [
        {{
            "learning_outcome": STR,
            "concept_ids": LIST[STR]
        }}
    ]
}}]
"""

concept_hierarchy_refine_content_prompt = PromptTemplate.from_template(
    concept_hierarchy_refine_content_prompt_str
)
concept_hierarchy_parse_prompt = PromptTemplate.from_template(
    concept_hierarchy_parse_prompt_str
)
concept_hierarchy_starter_prompt = PromptTemplate.from_template(
    concept_hierarchy_starter_prompt_str
)
topic_summary_prompt = PromptTemplate.from_template(topic_summary_prompt_str)
learning_outcomes_prompt = PromptTemplate.from_template(learning_outcomes_prompt_str)
learning_outcomes_parse_prompt = PromptTemplate.from_template(
    learning_outcomes_parse_prompt_str
)
learning_outcomes_stages_prompt = PromptTemplate.from_template(
    learning_outcomes_stages_prompt_str
)
learning_outcomes_stages_parse_prompt = PromptTemplate.from_template(
    learing_outcomes_stages_parse_prompt_str
)
