

__author__ = "Ujjwal Acharya and Vishnu Nadella"
__version__ = "2.1"


# Required Modules for DAS Implementation
from pyzbar.pyzbar import decode
import gspread
import streamlit as st
from PIL import Image

# Required Credentials for Google Sheets API Connection
gc = gspread.service_account(filename="das_credentials.json")
sh = gc.open_by_key("1nW4f8seohxA24AS7vWTsrvCawztF7HXe6dFHMt-T0v8")

# Page Configuration details for Streamlit
st.set_page_config(page_title='DigiAuth System', page_icon="DigiAuth Logo-Only.png", initial_sidebar_state = 'auto')

# Page Sidebar Configuration
st.sidebar.image("DigiAuth.gif") # Changed from html link to added .gif in repo
st.sidebar.markdown(
    """<div style="text-align:center"><strong>DigiAuth V2.0 </strong><br><br></div>""", unsafe_allow_html=True)

st.sidebar.markdown("""<div style="text-align: justify"> Hello there! This is an Authentication System built for checking in people at variuos events. Connected with a Google Sheets API, this app can seamlessly update status of attending people by scanning their QR Codes and mark them as <strong> Attended</strong>. Verification Systems are also in place to check whether duplicate QR Codes are shown for multiple entries at the venue. </div>""", unsafe_allow_html=True)

st.sidebar.markdown(
    '''<br><br><div style="text-align: center"><small>Developed by Ujjwal and Vishnu  | Jan 2022 </small></div>''', unsafe_allow_html=True)


#Page Title
st.title("Digital Authentication System")


# Searching for target in sheets using Binary Search
def search(low, mid, high, data_set, name, ID, c):
    # Accessing elements in sheets with the help of indentation since wks.get_all_values() will return list of lists
    while low <= high:
        mid = (high + low) // 2
        chk = data_set[mid][1][2:] # Checking Label
        # To overcome the error which is raised in below if statements because of the behaviour of Binary Search
        try: 
            chk = int(chk)
        except ValueError:
            chk = 0

        if int(chk) < int(ID[2:]):
            low = mid + 1
        
        elif int(chk) > int(ID[2:]):
            high = mid - 1
        
        elif int(chk) == int(ID[2:]):
            if data_set[mid][c] == "FALSE" and name == data_set[mid][2]:
                return True, 1, int(data_set[mid][0]) + 1
            elif data_set[mid][c] == "TRUE" and name == data_set[mid][2]:
                return True, 0, None
            elif name != data_set[mid][2]: # if some one cheats
                return False, 2, None
    else: # Failed to find that element
        return False, None, None

# Checks the status of the accuired data (from QR -> decoder function)
def status(sheet, data_1, data_2, data_3, c): # Searching using Linear Search
    wks = sh.get_worksheet(sheet)
    data_set = wks.get_all_values()
    low, mid = 0, 0
    high = len(data_set) - 1
    uqn_ID = data_1
    name = data_2
    required, sta, row = search(low, mid, high, data_set, name, uqn_ID, c)
    if required and sta == 1: # Successful scan of a valid and unused QR code
        wks.update_cell(row, c + 1, "TRUE")
        if c == 7:
            cell_coord = "H" + str(c + 1)
        elif c == 6:
            cell_coord = "G" + str(c + 1)
        output = data_2 + ' attendance set to ' + wks.acell(cell_coord).value
        print(output)
        st.success(output)
        st.balloons()
        
        
    elif required and sta == 0: # When someone uses the same QR for the 2nd time
        output = data_2 + ' is already present!'
        print(output)
        st.error(output)
        

    elif sta == 2 or sta == None: # When someone creates their own QR code
        output = 'QR Not Matching with Database ' + str(data_1) + " " + str(data_2) + " " + str(data_3)
        print(output)
        print(data_1, data_2, data_3)
        st.error(output)
    else: # Worst Case sceneario
        output = "Program is dead..."
        print(output)
        st.error(output)
        
# Decodes the QR code and directs to appropriate sub sheet
def decoder(image):
    qrCode = decode(image) #decoded QR code
    stat = 0
    for obj in qrCode:
        stat = 1
        barcodeData = obj.data.decode("utf-8")
        data_1, data_2, data_3 = map(str, barcodeData.split('\n'))
        if int(data_3[:5]) == 20951:
            status(1, data_1, data_2, data_3, 7)
        elif int(data_3[:5]) == 21955:
            status(2, data_1, data_2, data_3, 6)
        elif int(data_3[:5]) == 21951:
            status(0, data_1, data_2, data_3, 7)
        else:
            output = "Provided QR code is Invalid"
            print(output)
            st.error(output)
            
    else:
        if stat == 0:   # This if ladder is for overcoming a bug that's caused by for else
            st.error("No QR code has been detected or recognized. Take a new picture!")
        elif stat == 1:
            stat = 0


# Declaring empty variable for printing output messages
message = st.empty()

# Camera Input Setup
startcam = st.camera_input('Scan QR Code')

if startcam:
    img = Image.open(startcam)
    decoder(img)


# Hiding Streamlit Components which are not necessary
hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """
st.markdown(hide_st_style, unsafe_allow_html=True)
st.markdown("""<title> DigiAuth System </title>""", unsafe_allow_html=True)
