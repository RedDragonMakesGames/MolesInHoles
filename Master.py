import SetUpScreen
import MolesInHoles

#Run the set up screen
setUpScreen = SetUpScreen.SetUp()
boardsetup = setUpScreen.Run()
game = MolesInHoles.MolesInHoles(boardsetup)
#Restart the board if the restart button was pressed
while game.Run() == True:
    board = game = MolesInHoles.MolesInHoles(boardsetup)