local increment = tonumber(ARGV[1])
local results = {}

for i = 2, #ARGV do
    local key = ARGV[i]

    -- Check if the key exists
    if redis.call("EXISTS", key) == 1 then
        -- Key exists, increment it by the provided value
        local incrementedValue = redis.call("INCRBY", key, increment)
        table.insert(results, {key, incrementedValue})
    end
end

return results
