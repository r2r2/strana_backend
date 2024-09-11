local increment = tonumber(ARGV[1])
local results = {}

for i = 2, #ARGV do
    local key = ARGV[i]

    if redis.call("EXISTS", key) == 1 then
        local decrementedValue = redis.call("DECRBY", key, increment)
        table.insert(results, {key, decrementedValue}) 
    end
end

return results
