class Instance():
    def __init__(self, n, f, c, d):
        self.n = n
        self.f = f
        self.c = c
        self.d = d
    
    def load_from_file(file_path):
        with open(file_path, 'r') as file:
            n = int(file.readline().strip())
            f = list(map(int, file.readline().strip().split(',')))
            c = list(map(int, file.readline().strip().split(',')))
            d = int(file.readline().strip())
        return Instance(n, f, c, d)
    
    @classmethod
    def from_csv(cls, file_path):
        return cls.load_from_file(file_path)
    
    def __str__(self):
        return f"Instance(n={self.n}, f={self.f}, c={self.c}, d={self.d})"
    
    def __repr__(self):
        return self.__str__()