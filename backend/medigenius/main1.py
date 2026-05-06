from tools.search_tools import get_tavily_search, get_wikipedia_wrapper 

tavily = get_tavily_search()
wikipedia = get_wikipedia_wrapper()

# Test Wikipedia
print(wikipedia.run("Artificial Intelligence"))

# Test Tavily
#print(tavily.invoke("Latest AI news"))