import datetime

class File:
    def __init__(self, name, content=''):
        self.name = name
        self.type = self.name.partition(".")[2]
        self.content = content
        self.size = len(content)
        self.created_at = datetime.datetime.now()
        self.modified_at = self.created_at
        self.open_mode = None

    def open(self, mode):
        if self.open_mode is not None:
            return f"File {self.name} is already open"
        self.open_mode = mode
        return f"File {self.name} succesfully opened in {mode} mode"

    def close(self):
        if self.open_mode is None:
            return f"File {self.name} is not open"
        self.open_mode = None
        return f"File {self.name} succesfully closed"

    def write(self, data):
        if self.open_mode is None or 'w' not in self.open_mode and 'a' not in self.open_mode:
            return f"File {self.name} not open in write or append mode"
        self.content += data
        self.size += len(data)
        self.modified_at = datetime.datetime.now()
        return f"Successfuly written to file {self.name}"

    def write_at(self, offset, data):
        if self.open_mode is None or 'w' not in self.open_mode and 'a' not in self.open_mode:
            return f"File {self.name} not open in write or append mode"
        if offset < 0 or offset > len(self.content):
            return "Invalid offset"
        self.content = self.content[:offset] + data + self.content[offset:]
        self.size += len(data)
        self.modified_at = datetime.datetime.now()
        return f"Successfuly written to file {self.name}"

    def read(self):
        if self.open_mode is not None and 'r' not in self.open_mode:
            return "File {self.name} not open in read mode"
        return self.content

    def read_at(self, offset, length):
        if self.open_mode is not None and 'r' not in self.open_mode:
            return "File {self.name} not open in read mode"
        if offset < 0 or offset > len(self.content):
            return "Invalid offset"
        return self.content[offset:offset+length]

    def truncate(self, size=None):
        if self.open_mode is not None:
            return "File {self.name} is open"
        if size is None:
            size = 0
        elif size < 0 or size > len(self.content):
            return "Invalid size"
        self.content = self.content[:size]
        self.size = size
        self.modified_at = datetime.datetime.now()
        return f"Successfuly truncated file {self.name}"

    def __repr__(self):
        return f"File('{self.name}')"

class Directory:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.created_at = datetime.datetime.now()
        self.modified_at = self.created_at
        self.contents = {}

    def add_file(self, file):
        self.contents[file.name] = file
        self.modified_at = datetime.datetime.now()

    def add_directory(self, directory):
        directory.parent = self
        self.contents[directory.name] = directory
        self.modified_at = datetime.datetime.now()

    def get_file(self, name):
        if name in self.contents and isinstance(self.contents[name], File):
            return self.contents[name]
        return None

    def get_directory(self, name):
        if name in self.contents and isinstance(self.contents[name], Directory):
            return self.contents[name]
        return None

    def remove_file(self, file):
        del self.contents[file.name]
        self.modified_at = datetime.datetime.now()

    def remove_directory(self, directory):
        del self.contents[directory.name]
        self.modified_at = datetime.datetime.now()

    def __repr__(self):
        return f"Directory('{self.name}')"

class VirtualFileSystem:
    def __init__(self):
        self.root = Directory('root')
        self.current_directory = self.root
        self.memory = [[{} for _ in range(8)] for _ in range(8)]

    def create_file(self, name):
        file = File(name)
        if file.name in self.current_directory.contents:
            return f"{name} already exists in current directory"
        self.current_directory.add_file(file)
        return f"File created: {name}"

    def delete_file(self, name):
        file = self.current_directory.get_file(name)
        if file:
            self.current_directory.remove_file(file)
            return f"File deleted: {name}"
        else:
            return f"No such file: {name}"

    def create_directory(self, name):
        directory = Directory(name)
        if directory.name in self.current_directory.contents:
            return f"{name} already exists in current directory"
        self.current_directory.add_directory(directory)
        return f"Directory created: {name}"

    def delete_directory(self, name):
        directory = self.current_directory.get_directory(name)
        if directory:
            self.current_directory.remove_directory(directory)
            return f"Directory deleted: {name}"
        else:
            return f"No such directory: {name}"

    def change_directory(self, path):
        if path == '/':
            current_directory = self.root
        else:
            path_components = path.split('/')
            if path_components[0] == '':
                # Absolute path, start at the root directory
                current_directory = self.root
                path_components = path_components[1:]
            else:
                # Relative path, start at the current directory
                current_directory = self.current_directory
            for component in path_components:
                if component == '..':
                    # Move up one level in the directory structure
                    current_directory = current_directory.parent
                else:
                    # Move down one level in the directory structure
                    directory = current_directory.get_directory(component)
                    if directory:
                        current_directory = directory
                    else:
                        return f"No such directory: {component}"
        self.current_directory = current_directory
        return f"Successfuly moved to directory: {str(self.current_directory.name)}"

    def move_file(self, file_name, target_directory_name):
        called_directory = self.current_directory
        # Get the file to be moved
        file_to_move = self.current_directory.get_file(file_name)
        if not file_to_move:
            return f"No such file: {file_name}"
        self.change_directory(target_directory_name)
        # Remove the file from its current directory
        called_directory.remove_file(file_to_move)
        # Add the file to the target directory
        self.current_directory.add_file(file_to_move)
        self.current_directory = called_directory
        return f"{file_name} has been moved to {target_directory_name}"

    def calc_free_memory(self):
        count = 0
        for i in self.memory:
            for j in i:
                if j == {}:
                    count+=1
        return count
            
        
    def update_mmap(self, _file):
        ind = 0
        s = _file.read()
        for i in self.memory:
            while {} in i:
                if ind == len(s):
                    return
                for j in i:
                    if j == {}:
                        j.update({s[ind] : self.current_directory.name+", "+_file.name+", "+"block "+str(self.memory.index(i)+1)})
                        ind+=1
                        break
                    else:
                        continue
                continue

# main interactive loop
def terminal():
    vfs = VirtualFileSystem()
    while True:
        command = input(f"{vfs.current_directory.name}$ ")
        parts = command.split()

        # ignore no command
        if not parts:
            continue

        # list the details of current directory
        if parts[0] == "ls":
            print(f"{'name':15} {'type':10} {'size':10} {'mode':10} {'last_modified':19}")
            for item in vfs.current_directory.contents.values():
                if str(item)[:4] == "File":
                    print(f"{str(item.name):15} {str(item.type):10} {str(item.size)+'B':10} {str(item.open_mode):10} {str(item.modified_at)[:19]}")
                else:
                    print(f"{str(item.name):15} {'dir':10} {'-':10} {'-':10} {str(item.modified_at)[:19]}")

        # create file
        elif parts[0] == "create":
            if len(parts) != 2:
                print("Usage: create <name>")
                continue
            print(vfs.create_file(parts[1]))

        # delete file
        elif parts[0] == "delete":
            if len(parts) != 2:
                print("Usage: delete <name>")
                continue
            print(vfs.delete_file(parts[1]))

        # make directory
        elif parts[0] == "mkdir":
            if len(parts) != 2:
                print("Usage: mkdir <name>")
                continue
            print(vfs.create_directory(parts[1]))

        # delete directory
        elif parts[0] == "rmdir":
            if len(parts) != 2:
                print("Usage: rmdir <name>")
                continue
            print(vfs.delete_directory(parts[1]))

        # change directory
        elif parts[0] == "chdir":
            if len(parts) != 2:
                print("Usage: chdir <path>")
                continue
            print(vfs.change_directory(parts[1]))

        # move file to target directory
        elif parts[0] == "move":
            if len(parts) != 3:
                print("Usage: move <f_name> <path>")
                continue
            print(vfs.move_file(parts[1], parts[2]))

        # open file
        elif parts[0] == "open":
            if len(parts) != 3:
                print("Usage: open <name> <mode>")
                continue
            file = vfs.current_directory.get_file(parts[1])
            if file:
                if parts[2] == "w":
                    print(file.open("w"))
                elif parts[2] == "r":
                    print(file.open("r"))
                else:
                    print("Enter a valid mode to open file (r,w)")
            else:
                print(f"No such file: {parts[1]}")
                
        # close file
        elif parts[0] == "close":
            if len(parts) != 2:
                print("Usage: close <name>")
                continue
            file = vfs.current_directory.get_file(parts[1])
            if file:
                print(file.close())
            else:
                print(f"No such file: {parts[1]}")

        # write to file
        elif parts[0] == "write_to_file":
            if len(parts) !=3 and len(parts) != 4:
                print("Usage: write_to_file <name> <data> <offset>")
                continue
            if vfs.calc_free_memory() < len(parts[2]):
                print("Cannot write to file as memory is full")
                continue
            file = vfs.current_directory.get_file(parts[1])
            if file:
                if len(parts) == 3:
                    print(file.write(parts[2]))
                    file.close()
                    file.open("r")
                    vfs.update_mmap(file)
                    file.close()
                    file.open("w")
                elif len(parts) == 4:
                    offset = int(parts[3])
                    print(file.write_at(offset, parts[2]))
            else:
                print(f"No such file: {parts[1]}")

        # read from file
        elif parts[0] == "read_from_file":
            if len(parts) != 2 and len(parts) != 4:
                print("Usage: read_from_file <name> <offset> <length>")
                continue
            file = vfs.current_directory.get_file(parts[1])
            if file:
                if len(parts) == 2:
                    print(file.read())
                elif len(parts) == 4:
                    offset = int(parts[2])
                    length = int(parts[3])
                    print(file.read_at(offset, length))
            else:
                print(f"No such file: {parts[1]}")

        # truncate file
        elif parts[0] == "truncate":
            if len(parts) != 2 and len(parts) != 3:
                print("Usage: truncate <name> <size>")
                continue
            file = vfs.current_directory.get_file(parts[1])
            if file:
                size = int(parts[2]) if len(parts) == 3 else 0
                print(file.truncate(size))
            else:
                print(f"No such file: {parts[1]}")

        # display memory map
        elif parts[0] == "show_memory_map":
            count = 0
            for i in vfs.memory:
                for j in i:
                    if j == {}:
                        print("*", end="\t")
                    else:
                        print(j, end="\t")
                    count += 1
                    if count % 8 == 0:
                        print("\n")
            continue


        elif parts[0] == "help":
            print("Available commands:")
            print("  ls                                         List contents of current directory")
            print("  mkdir <name>                               Create new directory in current directory")
            print("  rmdir <name>                               Remove directory from current directory")
            print("  chdir <path>                               Change current directory. Set path as:")
            print("                                             ..      ==>     Move up directory")
            print("                                             /       ==>     Return to root")
            print("                                             /d/d    ==>     Absolute path")
            print("                                             d/d     ==>     Relative path")
            print("  create <name>                              Create new file in current directory")
            print("  delete <name>                              Remove file from current directory")
            print("  open <name> <mode>                         Open file in r or w mode")
            print("  close <name>                               Close file")
            print("  write_to_file <name> <data> <offset>       Write to file at a specific offset (optional)")
            print("  read_from_file <name> <offset> <length>    Read from file from a specific offset (optional)")
            print("  truncate <name> <size>                     Truncate file to a specified size (or all of it if not specified)")
            print("  show_memory_map                            Display Memory Map")
            print("  help                                       Display this help message")
            print("  exit                                       Exit the program")

        elif parts[0] == "exit":
            break
        else:
            print(f"Unknown command: {parts[0]}")

if __name__ == "__main__":
    terminal()