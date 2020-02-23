# -*- coding: utf-8 -*-

# python imports
import random

# chillin imports
from chillin_client import RealtimeAI

# project imports
from ks.models import ECell, EDirection, Position
from ks.commands import ChangeDirection, ActivateWallBreaker


class AI(RealtimeAI):

    def __init__(self, world):
        super(AI, self).__init__(world)


    def initialize(self):
        print('initialize')
        #here we can put some shit to initialize some variables
        #zeroth cycle
        #3000ms

    def decide(self):
        print('decide')
        #every cycle
        #500ms
        m = len(self.world.board[0])
        n = len(self.world.board)
        curX = self.world.agents[self.my_side].position.x
        curY = self.world.agents[self.my_side].position.y
        curDir = -1

        #Up0 Right1 Down2 Left3
        if curDir == EDirection.Left:
            curDir = 3
        if curDir == EDirection.Up:
            curDir = 0
        if curDir == EDirection.Right:
            curDir = 1
        if curDir == EDirection.Down:
            curDir = 2
        chooseList = []
        xDir = [0, 1, 0, -1]
        yDir = [-1, 0, 1, 0]
        Dir = [EDirection.Up, EDirection.Right, EDirection.Down, EDirection.Left]
        for i in range(4):
            if i != curDir:
                if curX + xDir[i] >= 0 and curY + yDir[i] >= 0:
                    if curX + xDir[i] < m and curY + yDir[i] < n:
                        if self.world.board[curY + yDir[i]][curX + xDir[i]] == ECell.Empty:
                            chooseList.append(Dir[i])
        self.send_command(ChangeDirection(random.choice(chooseList)))
