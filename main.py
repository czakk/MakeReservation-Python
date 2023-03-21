import client.utils
import client.methods
import sys



if __name__== '__main__':
    while True:
        match client.utils.choosing_menu(['Make reservation', 'Cancel a reservation', 'Print schedule', 'Save schedule '
                                                                                                         'to a file'],
                            '\nWhat do you want to do:'):
            case 0:
                client.methods.make_reservation()
            case 1:
                client.methods.cancel_reservation()
            case 2:
                client.methods.print_schedule()
            case 3:
                client.methods.save_to_file()
            case 4:
                print('Bye!')
                sys.exit()