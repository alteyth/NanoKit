from nanotec_nanolib import Nanolib
import time

# ============================================================ #
class ScanBusCallback(Nanolib.NlcScanBusCallback): # override super class
    def __init__(self):
        super().__init__()
    def callback(self, info, devicesFound, data):
        if info == Nanolib.BusScanInfo_Start :
            print('Scan started.')
        elif info == Nanolib.BusScanInfo_Progress :
            if (data & 1) == 0 :
                print('.', end='', flush=True)
        elif info == Nanolib.BusScanInfo_Finished :
            print('\nScan finished.')

        return Nanolib.ResultVoid()

callbackScanBus = ScanBusCallback() # Nanolib 2021
# ============================================================ #

def convert_to_signed_32bit(unsigned_integer):
    # Verifica se il numero unsigned è maggiore di 2^31 - 1
    if unsigned_integer > 0x7FFFFFFF:
        # Calcola il valore signed usando il complemento a due
        signed_integer = unsigned_integer - 0x100000000
    else:
        signed_integer = unsigned_integer
    
    return signed_integer

class NanoDevice:
    # Questo è la classe principale. Ha tutti i metodi necessari per la connessione e l'uso del controller
    def __init__(self):
        # Qui vengono istanziati i componenti necessari alla connessione e gestione del controller
        self.accessor: Nanolib.NanoLibAccessor = Nanolib.getNanoLibAccessor()
        self.accessor.setLoggingLevel(Nanolib.LogLevel_Off)
        self.device_handle: Nanolib.DeviceHandle
        bus: Nanolib.BusHardwareId


    def create_bus_hardware_options(self, bus_hw_id: Nanolib.BusHardwareId):
        # Questa funzione è standard e serve a creare le opzioni necessarie alla connessione al bus
        bus_hardware_option = Nanolib.BusHardwareOptions()
        
        if (bus_hw_id.getProtocol() == Nanolib.BUS_HARDWARE_ID_PROTOCOL_CANOPEN):
            # in case of CAN bus it is the baud rate
            bus_hardware_option.addOption(
                Nanolib.CanBus().BAUD_RATE_OPTIONS_NAME,
                Nanolib.CanBaudRate().BAUD_RATE_1000K
            )

            if (bus_hw_id.getBusHardware() == Nanolib.BUS_HARDWARE_ID_IXXAT):
                # in case of HMS IXXAT we need also bus number
                bus_hardware_option.addOption(
                    Nanolib.Ixxat().ADAPTER_BUS_NUMBER_OPTIONS_NAME, 
                    Nanolib.IxxatAdapterBusNumber().BUS_NUMBER_0_DEFAULT
                )
        
        elif (bus_hw_id.getProtocol() == Nanolib.BUS_HARDWARE_ID_PROTOCOL_MODBUS_RTU):
            # in case of Modbus RTU it is the serial baud rate
            bus_hardware_option.addOption(
                Nanolib.Serial().BAUD_RATE_OPTIONS_NAME,
                Nanolib.SerialBaudRate().BAUD_RATE_19200
            )
            # and serial parity
            bus_hardware_option.addOption(
                Nanolib.Serial().PARITY_OPTIONS_NAME,
                Nanolib.SerialParity().EVEN
            )
        else:
            pass           
        return bus_hardware_option
    
    def connect(self):
        # Questa è la funzione che si occupa di connettersi prima al bus e poi al dispositivo stesso (il controller)
        result_bus = self.accessor.listAvailableBusHardware()
        bus_ids = result_bus.getResult()

        # Scan dei Bus disponibili e scelta del nostro
        for id in bus_ids:
            if id.getName() == "USB Bus" and id.getProtocol() == "MODBUS VCP":
                self.bus = id
        bus_hw_options = self.create_bus_hardware_options(self.bus)

        # Apertura del Bus
        result_bus_open = self.accessor.openBusHardwareWithProtocol(self.bus, bus_hw_options)
        if(result_bus_open.hasError()):
            print("ERRORE nell'apertura del bus")
        else:
            print(f"Bus {self.bus.getName()} con protocollo {self.bus.getProtocol()} aperto con successo!")
        
        # Scan dei dispositivi disponibili
        result_device_scan = self.accessor.scanDevices(self.bus, callbackScanBus)
        if (result_device_scan.hasError()):
            print("ERRORE nello scan dei Devices!")
        device: Nanolib.DeviceId
        device_ids = result_device_scan.getResult()
        device = device_ids[0]
        self.device_handle = self.accessor.addDevice(device).getResult()

        # Connessione al dispositivo completata 
        result_device_connection = self.accessor.connectDevice(self.device_handle)
        if (result_device_connection.hasError()):
            print("ERRORE nella connessione al Device")
    
    def get_od_value(self, index, subindex = 0x00):
        # Questa funzione legge direttamente dall'Object Dictionary
        value = self.accessor.readNumber(self.device_handle, Nanolib.OdIndex(index, subindex)).getResult()
        value = convert_to_signed_32bit(value)
        return value

    def get_operation_mode(self):
        # Legge dall'Object Dictionary tramite la funzione precedente e indica la modalità operativa attuale
        value = self.get_od_value(0x6063)
        match value:
            case -2:
                print(f"Modalità Operativa Attuale: Auto Setup")
            case -1:
                print(f"Modalità Operativa Attuale: Clock-direction")
            case 0:
                print(f"Modalità Operativa Attuale: No Mode")
            case 1:
                print(f"Modalità Operativa Attuale: Profile Position")
            case 2:
                print(f"Modalità Operativa Attuale: Velocity")
            case 3:
                print(f"Modalità Operativa Attuale: Profile Velocity")
            case 4:
                print(f"Modalità Operativa Attuale: Profile Torque")
            case 5:
                print(f"Modalità Operativa Attuale: Reserved")
            case 6:
                print(f"Modalità Operativa Attuale: Homing")
            case 7:
                print(f"Modalità Operativa Attuale: Interpolated Position")
            case 8:
                print(f"Modalità Operativa Attuale: Cyclic Synchronous Position")
            case 9:
                print(f"Modalità Operativa Attuale: Cyclic Synchronous Velicty")
            case 10:
                print(f"Modalità Operativa Attuale: Cyclic Synchronous Torque")

    def rotate(self, duration, velocity):
        # Questa funzione fa girare il motore per il tempo indicato

        # Stoppa eventuali programmi NanoJ al momento in esecuzione sul controller
        self.accessor.writeNumber(self.device_handle, 0, Nanolib.OdIndex(0x2300, 0x00), 32)
        
        # Va in modalità Velocity
        self.accessor.writeNumber(self.device_handle, 3, Nanolib.OdIndex(0x6060, 0x00), 8)

        # Imposta la velocity
        self.accessor.writeNumber(self.device_handle, velocity, Nanolib.OdIndex(0x60FF, 0x00), 32)

        # Switcha la macchina a stati in "operation enabled"
        self.accessor.writeNumber(self.device_handle, 6, Nanolib.OdIndex(0x6040, 0x00), 16)
        self.accessor.writeNumber(self.device_handle, 7, Nanolib.OdIndex(0x6040, 0x00), 16)

        # Il motore gira per un tempo = time
        self.accessor.writeNumber(self.device_handle, 0xF, Nanolib.OdIndex(0x6040, 0x00), 16)
        time.sleep(duration)

        # Il motore viene fermato
        self.accessor.writeNumber(self.device_handle, 0, Nanolib.OdIndex(0x6040, 0x00), 16)

    def disconnect(self):
        # Qui viene disconnesso il dispositivo e chiuso il Bus
        self.accessor.disconnectDevice(self.device_handle)
        self.accessor.closeBusHardware(self.bus)