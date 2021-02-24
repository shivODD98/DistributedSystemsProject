class GroupCommunicator:

    def __init__(self):
        self.reader, self.writer = ''

    async def writeMsg(self, msg):
        self.writer.write(msg.encode('UTF-8'))
        await self.writer.drain()

    async def writeFile(self, file_path):
        source_file = open(file_path, 'rb')
        source_data = source_file.read()
        source_file.close()
        self.writer.write(source_data)
        await self.writer.drain()

    def closeWriter(self):
        self.writer.close
