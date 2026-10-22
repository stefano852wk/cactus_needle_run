"""Pre-download the Needle engine so it's cached in the Docker image."""

import needle

# Creating a Needle instance triggers the engine download from Hugging Face.
# We immediately close it — this is just to cache the .so file.
agent = needle.Needle(tools=[], weights="needle3.cact")
agent.close()
print("Needle engine downloaded and cached")
