from NanoKit import NanoDevice, UnitMapper

if __name__ == "__main__":
    controller = NanoDevice()
    unitMapper = UnitMapper()

    controller.connect()

    controller.get_operation_mode()

    controller.rotate(4, 50)

    controller.disconnect()
