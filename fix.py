from klasa import *

h = Haslo('aener')
s = h.listLangs[0]

print(s.content)

s.pola()

s.znaczeniaDetail[0][0] = s.znaczeniaDetail[0][0] + 'k'

s.saveChanges()

print(s.content)
