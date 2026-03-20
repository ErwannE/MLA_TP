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
    
    def extend_instance(self, new_n):
        d = new_n // 2
        f = [0] * new_n
        c = [0] * new_n
        f[0] = 7
        c[0] = 8
        for i in range(1, new_n):
            f[i] = f[i-1]*f[0] % 159
            c[i] = c[i-1] + c[0] % 61
        return Instance(new_n, f, c, d)
