#!/usr/bin/env python3
"""Quick progress checker for running tests"""
import time
import os

output_file = "/private/tmp/claude-501/-Users-abierschenk-Desktop-TableauRepos-tableau-langchain-tableau-langchain/0257f93b-722b-4622-9472-63125013f877/tasks/b30eya81b.output"

print("Monitoring test progress...\n")
print("=" * 80)

last_size = 0
while True:
    try:
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            if size > last_size:
                with open(output_file, 'r') as f:
                    content = f.read()
                    # Print only new content
                    if last_size > 0:
                        content = content[last_size:]
                    print(content, end='')
                last_size = size
        time.sleep(2)
    except KeyboardInterrupt:
        print("\n\nStopped monitoring.")
        break
    except Exception as e:
        print(f"Error: {e}")
        break
