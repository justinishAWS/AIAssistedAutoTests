# AIAssistedAutoTests
This can run Test #6 (from the APM demo status tracking Quip file) end-to-end with no user interaction.

We utilize custom Actions to authenticate and federate an AWS link automatically and inject JavaScript code to access metric graphs.

## Quick Start
To try running this on your local machine, ensure that you have at least `ReadOnly` access to the apm-demo1 acccount and run the following commands after cloning the repository:
1. Run `mwinit` to generate new credentials  

2. Run `ada credentials update --account=<apm-demo1_account_id> --provider=isengard --once --role=<Role>`

3. Run `pip install browser-use` to install browser-use
4. Run `pip install "browser-use[memory]"` to install memory functionality

5. Run `pip install playwright` to install PlayWright

6. Run the file with `python Test6.py`

## Prompt Engineering

If you plan to implement additional tests or use browser-use in other areas, to write a successful task, there are three important features to follow to create your prompt:

### 1. Structure
From looking at [previous examples](https://github.com/browser-use/awesome-prompts?tab=readme-ov-file), I found that the most effective way to structure a prompt is as follows:
1. **Steps:** Use numbered steps to split up complex tasks into subtasks
2. **Considerations:** Provide information the model should consider while executing the steps
3. **Additional important information:** Provide information to explain any ambiguous situations the model may face

The format should follow this structure:
```
<Task description> with the following steps:

1. <task 1>
2. <task 2>
3. <...>

Considerations:
- <Information to consider during execution>

<Important information to consider / adaptability information (what to do if the model gets confused)>
```

- For an in-depth example, look at `Test6.py` to understand how to use this structure to create your prompts

### 2. Clarity

To avoid ambiguity and vague instructions, it is important that you:

1. **Use simple language:** Keep language simple in your prompts
2. **Clearly state instructions:** Write specific and clear instructions in all of your steps
3. **Provide additional information:** Define specific rules and behaviours you want the agent to follow
 
**Bad example:**
```
Find a good tv:

1. Search for a tv
2. Find the best one
```

**Good example:**
```
Provide the TV with the highest customer ratings with the following steps:

1. Navigate to bestbuy.com.
2. Search for 'TV'.
3. Sort the results by customer rating.
4. Return the price and name of the top three products.
```

### 3. Parameters

We can include parameters in the `Agent` object to provide additional information and optimize the model. Below are important parameters that should be included in your implementation:
1. `message_context`: Use this to provide additional information about the task we are performing to help the LLM understand the task better
- Ex. `message_context="""You are a tester. Your job is to conduct tests."""`
2. `extend_system_message`: Use this to add additional instructions to the default system prompt
- Ex. `extend_system_message= """REMEMBER it is ok if the test fails. When the test result is determined, DO NOT continue steps!!! JUST EXIT!!!"""`
