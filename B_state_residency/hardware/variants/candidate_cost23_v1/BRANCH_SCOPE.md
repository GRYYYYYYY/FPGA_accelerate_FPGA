# Additional branch gate scope

The standalone cost23_inputs branch test uses mocked coordinate replies and the same actual geometry/cost generated RTL plus collectors as the joined pilot/full gate. It exercises different-SLR detour and Y correction, equal-SLR skipping columns, noncross skipping all table requests, explicit unsupported landmark-active stop, and upper16bit price-version drift during actual cost execution. Different/equal-SLR numerical results are checked independently with staged binary32 arithmetic.

The joined real profile has no crossSLR connections. Therefore this standalone test does not prove the new third coordinate arbiter client under actual crossSLR graph/label/table traffic. That joined stress remains required, together with true landmark data and fault/drain/reset/reload coverage. It cannot be combined with older nonzero-owner or real-route timing evidence to claim full router correctness or acceleration.
