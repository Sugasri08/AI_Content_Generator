from crewai import Task

def research_task(agent, topic):

    return Task(

        description=f"""
        Research the topic: {topic}

        Include:
        - Key insights
        - Trends
        - Important facts
        - Useful information

        Keep it concise.
        """,

        expected_output="Research summary.",

        agent=agent
    )


def writing_task(agent, topic, content_type, tone, word_count, context):

    return Task(

        description=f"""
        Create a {content_type} about "{topic}"

        Requirements:
        - Tone: {tone}
        - Around {word_count} words
        - Engaging content
        - Clear structure
        - Strong introduction
        - Strong conclusion

        If content type is:
        - Email → professional email
        - Instagram Caption → short catchy caption
        - LinkedIn Post → professional social content
        - Blog Post → detailed blog
        - YouTube Script → engaging script
        """,

        expected_output="Final content output.",

        agent=agent,

        context=[context]
    )