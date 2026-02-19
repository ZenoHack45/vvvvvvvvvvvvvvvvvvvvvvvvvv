-- [[ LLKV PRIVATE ENGINE - GITHUB HOSTED ]] --
local lp = game:GetService("Players").LocalPlayer

-- This function makes sure the script knows who you are
local function GetUser()
    return lp.Name
end

-- [[ THE MAIN FUNCTIONS ]] --
_G.LoadMusic = function()
    print("Loading King Von Music...")
    -- We use pcall so it doesn't crash if the require is down
    pcall(function()
        require(88812096580830):Hload(GetUser())
    end)
end

_G.LoadC00lkidd = function()
    print("Loading c00lkidd...")
    pcall(function()
        require(14125553864):Fire(GetUser(), "c00lkidd")
    end)
end

-- [[ AUTO-EXECUTE OPTIONS ]] --
-- If you want the music to play the SECOND you run the script, uncomment the line below:
-- _G.LoadMusic()

print("LLKV ENGINE LOADED FROM GITHUB. Use _G.LoadMusic() to start.")
