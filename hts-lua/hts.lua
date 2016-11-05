local ffi = require("ffi")
header = io.open("hts_concat.h"):read("*a")

local hts = ffi.load("hts")
ffi.cdef(header)

local Variant = ffi.metatype("bcf1_t", {
    __index = {
        start = function(t) return t.pos - 1 end,
        stop = function(t) 
            return t.pos - 1 + ffi.string(t.d.allele[0]):len() end,
        function(t, k) 
            return k
        end,
    },
    __tostring = function(t) 
        return string.format("%d-%d/%s/%s", t:start(), t:stop(),
            ffi.string(t.d.allele[0]), ffi.string(t.d.allele[1]))
    end,

    __gc = function(t)
        hts.bcf_destroy(t)
    end

})

local INFO = {}
INFO.mt = {
    __index = function(t, k)
        return _getinfo(t, k)
    end
}

function _getinfo(info, key)
    local info_t = hts.bcf_get_info(info.hdr, info.bcf, key)
    if info_t == ffi.NULL then return nil end
    if info_t.len == 1 then
        if info_t.type <= 3 then -- INT
            if (info_t.type == 1 and info_t.v1.i == -128) or 
               (info_t.type == 2 and info_t.v1.i == -32768) or 
               (info_t.type == 3 and info_t.v1.i == -2147483648) then
               return nil
            end
            return info_t.v1.i
        elseif info_t.type == 5 then
            --if hts.bcf_float_is_missing(info_t.v1.f) then return nil end
            return info_t.v1.f
        elseif info_t.type == 7 then
            local v = ffi.string(info_t.vptr, info_t.vptr_len)
            if v[0] == 0x7 then return nil end
            return v
        end

    end
end

function INFO.new(bcf, hdr)
    local t = {bcf=bcf, hdr=hdr}
    setmetatable(t, INFO.mt)
    return t
end

function bcf_init()
    return ffi.gc(hts.bcf_init(), hts.bcf_destroy)
end


while true do
    -- make a file metatype
    htf = hts.hts_open("vt.norm.vcf.gz", "r")
    hdr = hts.bcf_hdr_read(htf)

    while true do
        local bcf = bcf_init()
        ret = hts.bcf_read(htf, hdr, bcf)
        if ret < 0 then break end
        hts.bcf_unpack(bcf, 15)

        
        info = INFO.new(bcf, hdr)
        a, b, c = info["DP"], info["PQR"], info.DP
        print(a, b, c)

        print(bcf.rid, bcf.pos, bcf:start(), bcf:stop())
        print(bcf)
    end

    print("closing")
    hts.bcf_hdr_destroy(hdr)
    hts.hts_close(htf)
end
