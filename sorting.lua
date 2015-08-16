local francuski = {
	["À"] = "A",
	["Â"] = "A",
	["Ç"] = "C",
	["É"] = "E",
	["È"] = "E",
	["Ë"] = "E",
	["Ê"] = "E",
	["Î"] = "I",
	["Ï"] = "I",
	["Ô"] = "O",
	["Œ"] = "OE",
	["Ù"] = "U",
	["Ú"] = "U",
	["Û"] = "U",
	["à"] = "a",
	["â"] = "a",
	["ç"] = "c",
	["é"] = "e",
	["è"] = "e",
	["ë"] = "e",
	["ê"] = "e",
	["î"] = "i",
	["ï"] = "i",
	["ô"] = "o",
	["œ"] = "oe",
	["ù"] = "u",
	["ú"] = "u",
	["û"] = "u",
}

local indexing = {
	["francuski"] = francuski
}

function p.stripAccents( frame )
	local language = frame.args[1]
	local text = frame.args[2]

	local indexing = indexing[ language ]

        if indexing == nil then
            return text
	end

	local result
        
	for codepoint in mw.ustring.gcodepoint( text ) do
            local unstripped = mw.ustring.char(codepoint)
            local stripped = indexing[ unstripped ]

            result = result .. changed
        end
        return result
end
return p
