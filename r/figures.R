require(ggplot2)
source("methods.R")

figures <- function(file_prefix) {
	print(sprintf("Running results set %s", file_prefix))
	alspac = grepl("alspac", file_prefix)

	results_file = sprintf("../results/%s_women.csv", file_prefix)
	params_file = sprintf("../results/%s_params.csv", file_prefix)

	df = read.csv(results_file, all=TRUE)
	params = read.csv(params_file, all=TRUE)

	df <- merge(x=df, y=params, by.x="parameters", by.y="hash", all.x=TRUE)

	do_figures(df, alspac)

}

do_figures <- function(df, alspac) {
	# Loop over games
	for(g in unique(df$game)) {
		# Loop over signaller types
		for(a in unique(df$decision_rule_signaller)) {
			print(sprintf("Running game %s, with rule %s, alspac = %s", toString(g), toString(a), alspac))
			d <- subset(df, df$game == g & df$decision_rule_signaller == a)
			signals(d, alspac)
			complete(d, alspac)
		}

	}
}

complete <- function(df, alpsac) {
	target = directories(as.character(df$game)[1], alspac, as.character(df$decision_rule_signaller)[1])
	finished = sprintf("%s/finished.png", target)
	referred = sprintf("%s/referred.png", target)
	print(sprintf("Writing %s & %s", finished, referred))
	png(finished)
	print(finished_by_type(df))
	dev.off()
	png(referred)
	print(referred_by_type(df))
	dev.off()
}

directories <- function(game, alspac, rule) {
	target = "../figures/%s/"
	dir.create(sprintf(target, game))
	if(alspac) {
		target = sprintf("%salspac/", target)
	}
	target = sprintf(target, game)
	dir.create(target)
	target = sprintf("%s%s", target, rule)
	dir.create(target)
	return(target)
}

signals <- function(df, alspac) {
	target = directories(as.character(df$game)[1], alspac, as.character(df$decision_rule_signaller)[1])
	target = sprintf("%s/%s", target, "signals_%s.png")
	for(i in 0:2) {
		print(sprintf("Writing %s", sprintf(target, i)))
		png(sprintf(target, i))
		print(signals_by_type(df, i))
		dev.off()
	}
}