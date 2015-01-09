

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

local lastAmt = -1
local lastExponent = -1
function math.Bias( x, biasAmt )
	if( lastAmt ~= biasAmt ) then
		lastExponent = math.log( biasAmt ) * -1.4427;
	end
	return math.pow( x, lastExponent );
end