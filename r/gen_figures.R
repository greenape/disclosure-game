source("figures.R")

files = c("referral", "referral_nested", "standard", "standard_nested", "referral_alspac", "referral_alspac_nested", "standard_alspac", "standard_alspac_nested_")
for(file in files) {
	figures(file)
}