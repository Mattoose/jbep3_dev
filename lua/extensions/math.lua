

require( "math" )

function math.clamp( val, a, b )
	if val > b then return b end
	if val < a then return a end
	return val
end

function math.RemapValClamped( val, A, B, C, D )
	if A == B then 
		if val >= b then
			return D
		else
			return C
		end
	end
	local cVal = (val - A) / (B - A);
	cVal = math.clamp( cVal, 0, 1 );

	return C + (D - C) * cVal;
end