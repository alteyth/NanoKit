from nanotec_nanolib import Nanolib

def convert_to_signed_32bit(unsigned_integer):
    # Verifica se il numero unsigned è maggiore di 2^31 - 1
    if unsigned_integer > 0x7FFFFFFF:
        # Calcola il valore signed usando il complemento a due
        signed_integer = unsigned_integer - 0x100000000
    else:
        signed_integer = unsigned_integer
    
    return signed_integer

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

def create_bus_hardware_options(bus_hw_id: Nanolib.BusHardwareId):

    bus_hardware_option = Nanolib.BusHardwareOptions()
    
    # now add all options necessary for opening the bus hardware
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

if __name__ == "__main__":
    accessor: Nanolib.NanoLibAccessor = Nanolib.getNanoLibAccessor()
    accessor.setLoggingLevel(Nanolib.LogLevel_Off)
    result_bus = accessor.listAvailableBusHardware()
    bus_ids = result_bus.getResult()

    bus: Nanolib.BusHardwareId

    for id in bus_ids:
        if id.getName() == "USB Bus" and id.getProtocol() == "MODBUS VCP":
            bus = id

    bus_hw_options = create_bus_hardware_options(bus)

    result_bus_open = accessor.openBusHardwareWithProtocol(bus, bus_hw_options)
    if(result_bus_open.hasError()):
        print("ERRORE nell'apertura del bus")
    else:
        print(f"Bus {bus.getName()} con protocollo {bus.getProtocol()} aperto con successo!")

    result_device_scan = accessor.scanDevices(bus, callbackScanBus)
    if (result_device_scan.hasError()):
        print("ERRORE nello scan dei Devices!")
    device: Nanolib.DeviceId
    device_ids = result_device_scan.getResult()
    device = device_ids[0]
    #Test Commit
    
    device_handle = accessor.addDevice(device).getResult()
    result_device_connection = accessor.connectDevice(device_handle)
    if (result_device_connection.hasError()):
        print("ERRORE nella connessione al Device")

    result_read = accessor.readNumber(device_handle, Nanolib.OdIndex(0x6061, 0x00)).getResult()
    print(f"\nModalità Operativa: {result_read}")

    result_read = accessor.readNumber(device_handle, Nanolib.OdIndex(0x6064, 0x00)).getResult()
    result_signed = convert_to_signed_32bit(result_read)
    print(f"\nPosizione Reale: {result_signed}")

    result_read = accessor.readNumber(device_handle, Nanolib.OdIndex(0x6063, 0x00)).getResult()
    result_signed = convert_to_signed_32bit(result_read)
    print(f"\nPosizione Interna: {result_signed}")

    accessor.disconnectDevice(device_handle)
    accessor.closeBusHardware(bus)