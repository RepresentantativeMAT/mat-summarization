import sys
import os

# Add the project root to sys.path if not running from root module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from method.MATSG import MATSG
from method.MATSGT import MATSGT
from method.MUITAS import MUITAS
from model.Feature import Feature

def test(user):
    
    matsgf = MATSGT(
        trc=0.05, #? Tenho q olhar pra esse cara
        trv=0.05,
        path="data/input/foursquare_user_" + str(user) + ".csv"
    )
    
    matsgf.execute(
        dir="data/output/foursquare_full/", 
        file="fq_u" + str(user) + "_MATSGT_out", 
        lst_categorical_pd=['price'],
        values_null=['-1'], 
        ignore_columns=None,
        pattern_date_input='?', 
        rc=0.05,
        # features=[('weather',), ('day',), ('category',), ('rating',), ('price',)]
        features=[('weather',), ('day',), ('category', 'price'), ('category', 'rating')]
    )
    print("Execution Finished for user " + str(user) + " !")

def test_for(start, ammount):
    all_users = [6, 7, 12, 14, 19, 25, 34, 50, 56, 65, 69, 70, 73, 80, 81, 82, 84, 90, 91, 94, 95, 99, 119, 120, 121, 138, 144, 150, 153, 154, 164, 171, 172, 178, 181, 182, 184, 185, 187, 188, 201, 207, 208, 236, 246, 254, 262, 267, 280, 293, 295, 315, 319, 343, 344, 347, 349, 354, 355, 359, 365, 371, 372, 384, 386, 390, 396, 398, 412, 422, 425, 432, 438, 439, 440, 443, 445, 448, 458, 461, 472, 474, 475, 484, 488, 492, 495, 509, 518, 519, 521, 527, 529, 531, 533, 539, 546, 553, 572, 579, 582, 585, 589, 593, 595, 596, 612, 617, 621, 628, 635, 638, 642, 643, 645, 646, 647, 649, 652, 660, 662, 673, 682, 688, 689, 699, 702, 705, 706, 708, 718, 722, 723, 730, 734, 742, 744, 745, 750, 752, 753, 754, 763, 766, 767, 768, 773, 787, 806, 816, 819, 820, 827, 834, 842, 857, 868, 872, 877, 881, 882, 885, 889, 891, 895, 900, 901, 902, 913, 916, 922, 928, 934, 943, 951, 974, 976, 980, 988, 990, 992, 1006, 1016, 1017, 1019, 1025, 1029, 1040, 1044, 1047, 1054, 1055, 1070]
    if ammount == 'full':
        ammount = len(all_users)
    for i in range(start, ammount + start):
        test(all_users[i])
        print(i + 1, 'done.', ammount - (i + 1), 'to go.')


if __name__ == "__main__":
    test_for(0, 'full')


