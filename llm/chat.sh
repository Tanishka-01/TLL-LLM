#!/usr/bin/env bash
cd "$(dirname "$0")"
source env/bin/activate

echo "================================"
echo "  Voice Assistant"
echo "  Type 'quit' to exit"
echo "================================"
echo ""

while true; do
    read -p "You: " QUESTION
    
    # Exit
    if [ "$QUESTION" = "quit" ] || [ "$QUESTION" = "exit" ]; then
        echo "Goodbye!"
        break
    fi
    
    # Skip empty input
    if [ -z "$QUESTION" ]; then
        continue
    fi
    
    # Auto-detect: math or system
    if echo "$QUESTION" | grep -qiE "plus|minus|add|subtract|multiply|divide|sum|difference|\+|\-|\*|\/|calculate|[0-9].*[0-9]"; then
        sed -i 's/function_group=.*/function_group="arithmetic"/' project_script.sh
    else
        sed -i 's/function_group=.*/function_group="system"/' project_script.sh
    fi
    
    echo ""
    ./project_script.sh "$QUESTION"
    echo ""
done
