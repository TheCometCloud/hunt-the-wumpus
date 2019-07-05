# Written by Nicholas Hanley
# Based on Gregory Yob's original BASIC
# Playtested by Nicolas Payton and Andrew Horvath

import random

cave = [
    [1, 4, 7],
    [0, 2, 9],
    [1, 3, 11],
    [2, 4, 13],
    [0, 3, 5],
    [4, 6, 14],
    [5, 7, 16],
    [0, 6, 8],
    [7, 9, 17],
    [1, 8, 10],
    [9, 11, 18],
    [2, 10, 12],
    [11, 13, 19],
    [3, 12, 14],
    [5, 13, 15],
    [14, 16, 19],
    [6, 15, 17],
    [8, 16, 18],
    [10, 17, 19],
    [12, 15, 1],
]

instructions = """WELCOME TO 'HUNT THE WUMPUS'
  THE WUMPUS LIVES IN A CAVE OF 20 ROOMS. EACH ROOM
HAS 3 TUNNELS LEADING TO OTHER ROOMS. (LOOK AT A
DODECAHEDRON TO SEE HOW THIS WORKS-IF YOU DON'T KNOW
WHAT A DODECAHEDRON IS, ASK SOMEONE)

     HAZARDS:
 BOTTOMLESS PITS - TWO ROOMS HAVE BOTTOMLESS PITS IN THEM
     IF YOU GO THERE, YOU FALL INTO THE PIT (& LOSE!)
 SUPER BATS - TWO OTHER ROOMS HAVE SUPER BATS. IF YOU
     GO THERE, A BAT GRABS YOU AND TAKES YOU TO SOME OTHER
     ROOM AT RANDOM. (WHICH MIGHT BE TROUBLESOME)

     WUMPUS:
 THE WUMPUS IS NOT BOTHERED BY THE HAZARDS (HE HAS SUCKER
 FEET AND IS TOO BIG FOR A BAT TO LIFT).  USUALLY
 HE IS ASLEEP. TWO THINGS WAKE HIM UP: YOUR ENTERING
 HIS ROOM OR YOUR SHOOTING AN ARROW.
     IF THE WUMPUS WAKES, HE MOVES (P=.75) ONE ROOM
 OR STAYS STILL (P=.25). AFTER THAT, IF HE IS WHERE YOU
 ARE, HE EATS YOU UP (& YOU LOSE!)

     YOU:
 EACH TURN YOU MAY MOVE OR SHOOT A CROOKED ARROW
   MOVING: YOU CAN GO ONE ROOM (THRU ONE TUNNEL)
   ARROWS: YOU HAVE 5 ARROWS. YOU LOSE WHEN YOU RUN OUT.
   EACH ARROW CAN GO FROM 1 TO 5 ROOMS. YOU AIM BY TELLING
   THE COMPUTER THE ROOM#S YOU WANT THE ARROW TO GO TO.
   IF THE ARROW CAN'T GO THAT WAY (IE NO TUNNEL) IT MOVES
   AT RAMDOM TO THE NEXT ROOM.
     IF THE ARROW HITS THE WUMPUS, YOU WIN.
     IF THE ARROW HITS YOU, YOU LOSE.

    WARNINGS:
     WHEN YOU ARE ONE ROOM AWAY FROM WUMPUS OR HAZARD,
    THE COMPUTER SAYS:
 WUMPUS-  'I SMELL A WUMPUS'
 BAT   -  'BATS NEARBY'
 PIT   -  'I FEEL A DRAFT'
"""


class Game:
    def __init__(self):
        self.setup()

    def setup(self, keepLocations=False):
        if keepLocations:
            self.locations = self._locations.copy()
        else:
            self.generateLocations()
        self.arrows = 5

    def generateLocations(self):
        locations = []
        rooms = list(range(20))
        for _ in range(6):
            room = random.choice(rooms)
            rooms.remove(room)
            locations.append(room)
        self._locations = locations
        self.locations = locations.copy()

    def start(self):
        return self.printInstructionsPrompt()

    def printInstructionsPrompt(self):
        return "INSTRUCTIONS (Y-N)?", self.getInstructionsPromptAnswer

    def getInstructionsPromptAnswer(self, answer):
        title = "HUNT THE WUMPUS"
        answer = answer.upper()
        if answer == "Y":
            return (
                "\n".join(
                    (
                        instructions,
                        title,
                        "",
                        self.printLocationAndHazardWarnings(),
                        "",
                        self.printMoveOrShootPrompt(),
                    )
                ),
                self.getMoveOrShootAnswer,
            )
        if answer == "N":
            return (
                "\n".join(
                    (
                        title,
                        "",
                        self.printLocationAndHazardWarnings(),
                        "",
                        self.printMoveOrShootPrompt(),
                    )
                ),
                self.getMoveOrShootAnswer,
            )
        return self.printInstructionsPrompt()

    def printLocationAndHazardWarnings(self):
        room = self.locations[0]
        tunnels = cave[room]
        lines = []
        for item, location in enumerate(self.locations):
            for tunnel in tunnels:
                if tunnel != location:
                    continue
                if item == 1:
                    lines.append("I SMELL A WUMPUS!")
                elif item == 2 or item == 3:
                    lines.append("I FEEL A DRAFT")
                elif item == 4 or item == 5:
                    lines.append("BATS NEARBY!")
        lines.append("YOU ARE IN ROOM  {}".format(room + 1))
        lines.append("TUNNELS LEAD TO  {}  {}  {}".format(*(t + 1 for t in tunnels)))
        return "\n".join(lines)

    def printMoveOrShootPrompt(self):
        return "SHOOT OR MOVE (S-M)?"

    def getMoveOrShootAnswer(self, answer):
        answer = answer.upper()
        if answer == "S":
            return self.printShootNumOfRoomsPrompt(), self.getShootNumOfRoomsAnswer
        if answer == "M":
            return self.printMovePrompt(), self.getMoveAnswer
        return self.printMoveOrShootPrompt(), self.getMoveOrShootAnswer

    def printShootNumOfRoomsPrompt(self):
        return "NO. OF ROOMS(1-5)?"

    def getShootNumOfRoomsAnswer(self, answer):
        try:
            answer = int(answer)
        except ValueError:
            return self.printShootNumOfRoomsPrompt(), self.getShootNumOfRoomsAnswer
        if answer < 1 or answer > 5:
            return self.printShootNumOfRoomsPrompt(), self.getShootNumOfRoomsAnswer
        nrooms = answer
        path = []

        def printShootRoomNumberPrompt():
            return "ROOM #?"

        def getShootRoomNumberAnswer(answer):
            nonlocal nrooms, path
            try:
                answer = int(answer)
            except ValueError:
                return printShootRoomNumberPrompt(), getShootRoomNumberAnswer
            if answer < 1 or answer > 20:
                return printShootRoomNumberPrompt(), getShootRoomNumberAnswer
            answer -= 1
            if len(path) > 1 and answer == path[len(path) - 1]:
                return (
                    "\n".join(
                        (
                            "ARROWS AREN'T THAT CROOKED - TRY ANOTHER ROOM",
                            printShootRoomNumberPrompt(),
                        )
                    ),
                    getShootRoomNumberAnswer,
                )
            path.append(answer)
            nrooms -= 1
            if nrooms > 0:
                return printShootRoomNumberPrompt(), getShootRoomNumberAnswer
            self.arrows -= 1
            room = self.locations[0]
            for p in path:
                tunnels = cave[room]
                for tunnel in tunnels:
                    if p == tunnel:
                        room = p
                        break
                else:
                    room = random.choice(tunnels)
                if room == self.locations[1]:
                    return (
                        "\n".join(
                            (
                                "AHA! YOU GOT THE WUMPUS!",
                                self.printWinMessage(),
                                self.printRestartPrompt(),
                            )
                        ),
                        self.getRestartAnswer,
                    )
                if room == self.locations[0]:
                    return (
                        "\n".join(
                            (
                                "OUCH! ARROW GOT YOU!",
                                self.printLoseMessage(),
                                self.printRestartPrompt(),
                            )
                        ),
                        self.getRestartAnswer,
                    )
            msg = self.moveWumpus()
            if msg != None:
                return (
                    "\n".join(
                        (
                            "MISSED",
                            msg,
                            self.printLoseMessage(),
                            self.printRestartPrompt(),
                        )
                    ),
                    self.getRestartAnswer,
                )
            if self.arrows == 0:
                return (
                    "\n".join(
                        ("MISSED", self.printLoseMessage(), self.printRestartPrompt())
                    ),
                    self.getRestartAnswer,
                )
            return (
                "\n".join(
                    (
                        "MISSED",
                        "",
                        self.printLocationAndHazardWarnings(),
                        "",
                        self.printMoveOrShootPrompt(),
                    )
                ),
                self.getMoveOrShootAnswer,
            )

        return printShootRoomNumberPrompt(), getShootRoomNumberAnswer

    def moveWumpus(self):
        room = self.locations[1]
        self.locations[1] = random.choice([room, *cave[room]])
        if self.locations[1] == self.locations[0]:
            return "TSK TSK TSK- WUMPUS GOT YOU!"

    def printLoseMessage(self):
        return "HA HA HA - YOU LOSE!"

    def printWinMessage(self):
        return "HEE HEE HEE - THE WUMPUS'LL GETCHA NEXT TIME!!"

    def printMovePrompt(self):
        return "WHERE TO?"

    def getMoveAnswer(self, answer):
        room = self.locations[0]
        try:
            dest = int(answer) - 1
        except ValueError:
            return self.printMovePrompt(), self.getMoveAnswer
        if dest not in cave[room] and dest != room:
            return "NOT POSSIBLE -" + self.printMovePrompt(), self.getMoveAnswer
        self.locations[0] = room = dest
        msg = ""
        if room == self.locations[1]:
            msg += "\n...OOPS! BUMPED A WUMPUS!"
        s = self.moveWumpus()
        if s != None:
            return (
                "\n".join((msg, s, self.printLoseMessage(), self.printRestartPrompt())),
                self.getRestartAnswer,
            )
        if room == self.locations[2] or room == self.locations[3]:
            return (
                "\n".join(
                    (
                        "",
                        "YYYIIIIEEEE . . . FELL IN PITS",
                        self.printLoseMessage(),
                        self.printRestartPrompt(),
                    )
                ),
                self.getRestartAnswer,
            )
        if room == self.locations[4] or room == self.locations[5]:
            self.locations[0] = random.randrange(20)
            m, state = self.getMoveAnswer(str(self.locations[0] + 1))
            return (
                "\n".join(("", "ZAP--SUPER BAT SNATCH! ELSEWHEREVILLE FOR YOU!", m)),
                state,
            )
        return (
            "\n".join(
                (
                    "",
                    self.printLocationAndHazardWarnings(),
                    "",
                    self.printMoveOrShootPrompt(),
                )
            ),
            self.getMoveOrShootAnswer,
        )

    def printRestartPrompt(self):
        return "TRY AGAIN (Y-N)?"

    def getRestartAnswer(self, answer):
        answer = answer.upper()
        if answer == "Y":
            return self.printSameSetupPrompt(), self.getSameSetupAnswer
        if answer == "N":
            return "", None
        return self.printRestartPrompt(), self.getRestartAnswer

    def printSameSetupPrompt(self):
        return "SAME SET-UP (Y-N)?"

    def getSameSetupAnswer(self, answer):
        answer = answer.upper()
        if answer == "Y":
            self.setup(keepLocations=True)
        elif answer == "N":
            self.setup()
        return self.getInstructionsPromptAnswer("N")
