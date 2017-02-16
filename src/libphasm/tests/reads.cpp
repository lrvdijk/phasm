#include <seqan/basic.h>
#include <seqan/sequence.h>
#include <phasm/alignments.h>
#include <catch.hpp>

using seqan::DnaString;

TEST_CASE("Reads have proper length", "[reads]") {
    REQUIRE(phasm::Read<DnaString>("id", 10).length() == 10);
    REQUIRE(phasm::Read<DnaString>("id", "ACTGATCGCA").length() == 10);
}
