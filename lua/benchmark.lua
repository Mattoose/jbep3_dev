-- From http://lua-users.org/lists/lua-l/1999-07/msg00087.html
-- Lua 5.2 took around 7 seconds
-- LuaJIT takes 0.13

function sieve(n)
  x = {}
  iter = 0
  repeat
    x[1] = 0
    i = 2
    repeat
      x[i] = 1
      i = i + 1
    until i > n
    p = 2
    while(p * p <= n) do
      j = p
      while(j <= n) do
        x[j] = 0
        j = j + p
      end
      repeat
        p = p + 1
      until x[p] == 1
    end
    iter = iter + 1
  until iter == 101
end

print("Sieve of Eratosthenes\n")
print("Start testing .....\n")
start = util.ModuleTime()
sieve(100000)
stop = util.ModuleTime()
print("Done!\n")
print("Total Time = "..(stop - start).."\n")