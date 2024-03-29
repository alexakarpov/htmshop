#!/usr/bin/env bash

SESSIONNAME="HTM_shop_WIP"
tmux has-session -t $SESSIONNAME &> /dev/null

if [ $? != 0 ]
 then
    tmux new -s $SESSIONNAME -d
    tmux split-window -h -t $SESSIONNAME
    window=${session}:0
    pane=${window}.0
    tmux send-keys -t "$pane" C-b 'poetry run ./manage.py runserver' Enter
    pane=${window}.1
    tmux select-pane -t "$pane"
    # tmux send-keys -t "$pane" C-b 'npx cypress open' Enter
fi

tmux attach -t $SESSIONNAME
