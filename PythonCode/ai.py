# -*- coding: utf-8 -*-

# python imports
import random

# chillin imports
from chillin_client import RealtimeAI

# project imports
from ks.models import ECell, EDirection, Position
from ks.commands import ChangeDirection, ActivateWallBreaker

from collections import deque

class AI(RealtimeAI):

    def __init__(self, world):
        super(AI, self).__init__(world)


    def initialize(self):
        print('initialize')
        self.m = len(self.world.board[0])
        self.n = len(self.world.board)
        self.xDir = [0, 1, 0, -1]
        self.yDir = [-1, 0, 1, 0]

    def convertDirToInd(self, curDir):
        #Up0 Right1 Down2 Left3
        if curDir == EDirection.Up:
            return 0
        if curDir == EDirection.Right:
            return 1
        if curDir == EDirection.Down:
            return 2
        if curDir == EDirection.Left:
            return 3

    def convertIndToDir(self, curDir):
        foo = [EDirection.Up, EDirection.Right, EDirection.Down, EDirection.Left]
        return foo[curDir]

    def isValidPos(self, x, y):
        return self.m > x >= 0 and self.n > y >= 0

    def getOppPos(self):
        return [self.world.agents[self.other_side].position.x, self.world.agents[self.other_side].position.y]

    def isEmpty(self, x, y):
        return self.world.board[y][x] == ECell.Empty and self.getOppPos() != [x, y]
    
    def numberOfEmptyNeighbors(self, x, y):
        ans = 0
        for i in range(4):
            newX = x + self.xDir[i]
            newY = y + self.yDir[i]
            if self.isValidPos(newX, newY) and self.isEmpty(newX, newY):
                ans += 1
        return ans

    def emptyNeighbors(self, x, y):
        ans = []
        xDir = [0, 1, 0, -1]
        yDir = [-1, 0, 1, 0]
        for i in range(4):
            newX = x + self.xDir[i]
            newY = y + self.yDir[i]
            if self.isValidPos(newX, newY) and self.isEmpty(newX, newY):
                ans.append(i)
        return ans

    def playerWallNeighbors(self, x, y):
        ans = []
        xDir = [0, 1, 0, -1]
        yDir = [-1, 0, 1, 0]
        for i in range(4):
            newX = x + self.xDir[i]
            newY = y + self.yDir[i]
            if self.isValidPos(newX, newY) and self.world.board[newY][newX] in [ECell.BlueWall, ECell.YellowWall]:
                ans.append(i)
        return ans

    def notAreaWallNeighbors(self, x, y):
        ans = []
        xDir = [0, 1, 0, -1]
        yDir = [-1, 0, 1, 0]
        for i in range(4):
            newX = x + self.xDir[i]
            newY = y + self.yDir[i]
            if self.isValidPos(newX, newY) and self.world.board[newY][newX] != ECell.AreaWall:
                ans.append(i)
        return ans
                
    def opposite(self, curDir): #returns ind
        if curDir == EDirection.Up:
            return 2
        if curDir == EDirection.Right:
            return 3
        if curDir == EDirection.Down:
            return 0
        if curDir == EDirection.Left:
            return 1

    def reachableSpace(self, x, y, curDir):
        originX = x
        originY = y
        x += self.xDir[curDir]
        y += self.yDir[curDir]
        queue = deque([[x, y]])
        mark = [[-1] * self.m for i in range(self.n)]
        mark[y][x] = 0
        ans = 1
        while len(queue) > 0:
            left = queue.popleft()
            for i in self.emptyNeighbors(left[0], left[1]):
                newX = left[0] + self.xDir[i]
                newY = left[1] + self.yDir[i]
                if mark[newY][newX] == -1 and (newX != originX or newY != originY):
                    queue.append([newX, newY])
                    ans += 1
                    mark[newY][newX] = mark[left[1]][left[0]] + 1
        print(ans)
        return ans

    def reachableEmptyWB(self, x, y, curDir):
        originX = x
        originY = y
        x += self.xDir[curDir]
        y += self.yDir[curDir]
        queue = deque([[x, y, 1]])
        mark = [[-1] * self.m for i in range(self.n)]
        mark[y][x] = 0
        while len(queue) > 0:
            left = queue.popleft()            
            for i in self.notAreaWallNeighbors(left[0], left[1]):
                newX = left[0] + self.xDir[i]
                newY = left[1] + self.yDir[i]
                if self.isEmpty(newX, newY) and (newX != originX or newY != originY):
                    return left[2] + 1
                if mark[newY][newX] == -1 and (newX != originX or newY != originY):
                    queue.append([newX, newY, left[2] + 1])
                    mark[newY][newX] = mark[left[1]][left[0]] + 1
        print("Not found")
        return float("inf")

    def mostOpenDecision(self, x, y, moves):
        ma = -1
        ans = -1
        for i in moves:
            newX = x + self.xDir[i]
            newY = y + self.yDir[i]
            cnt = self.numberOfEmptyNeighbors(newX, newY)
            if ma < cnt:
                ma = cnt
                ans = i
        return ans
    
    def decide(self):
        print('decide', self.current_cycle, self.my_side)
        #every cycle
        #500ms
        curX = self.world.agents[self.my_side].position.x
        curY = self.world.agents[self.my_side].position.y
        curDir = self.convertDirToInd(self.world.agents[self.my_side].direction)

        moves = self.emptyNeighbors(curX, curY)
        ma = -1
        betterMoves = []
        for i in moves:
            res = self.reachableSpace(curX, curY, i)
            if res > ma:
                ma = res
                betterMoves = [i]
            elif res == ma:
                betterMoves.append(i)
                
        if len(betterMoves) > 0:
            print("betterMoves: ", betterMoves)
            decision = self.mostOpenDecision(curX, curY, betterMoves)
        else:
            moves = self.playerWallNeighbors(curX, curY)
            res = [float("inf")] * 4
            mi = float("inf")
            ans = 0
            for i in moves:
                res[i] = self.reachableEmptyWB(curX, curY, i)
                if res[i] < mi:
                    mi = res[i]
                    ans = i
            print("res: ", res)
            print(self.convertIndToDir(ans), "WB")
            decision = ans
            if self.world.agents[self.my_side].wall_breaker_cooldown == 0:
                self.send_command(ActivateWallBreaker())
                
        self.send_command(ChangeDirection(self.convertIndToDir(decision)))
