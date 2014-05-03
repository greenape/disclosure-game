require(ggplot2)
source("methods.R")

figures <- function(file_prefix) {
	print(sprintf("Running results set %s", file_prefix))
	alspac = grepl("alspac", file_prefix)

	results_file = sprintf("../results/%s_women.csv.gz", file_prefix)
	params_file = sprintf("../results/%s_params.csv.gz", file_prefix)

	df = read.csv(results_file, all=TRUE)
	params = read.csv(params_file, all=TRUE)

	df <- merge(x=df, y=params, by.x="parameters", by.y="hash", all.x=TRUE)

	do_figures(df, alspac)

}

caseload_sqlite_figures_10 <- function() {
	print("Caseload_sqlite figures.")

	results_file = "../results/caseload_sqlite_low_prior__women.csv.gz"
	params_file = "../results/caseload_sqlite_low_prior__params.csv.gz"

	df = read.csv(results_file, all=TRUE)
	params = read.csv(params_file, all=TRUE)
	df <- merge(x=df, y=params, by.x="parameters", by.y="hash", all.x=TRUE)
	# Loop over games
	for(i in unique(interaction(df$mw_0, df$mw_1, df$mw_2))) {
		d <- subset(df, interaction(df$mw_0, df$mw_1, df$mw_2) == i)
		for(h in unique(d$parameters)) {
			c <- subset(d, d$parameters == h)
			game = sprintf("bias_10/caseload_sqlite/%s-%s", i, as.character(c$game)[1])
			target = directories(game, FALSE, as.character(c$decision_rule_signaller)[1])
			finished = sprintf("%s/finished.png", target)
			referred = sprintf("%s/referred.png", target)	
			do_complete(c, finished, referred)
			do_signals(c, sprintf("%s/%s", target, "signals_%s.png"))
		}
	}
}

caseload_sqlite_figures_20 <- function() {
	print("Caseload_sqlite figures.")

	results_file = "../results/caseload_sqlite_women.csv.gz"
	params_file = "../results/caseload_sqlite_params.csv.gz"

	df = read.csv(results_file, all=TRUE)
	params = read.csv(params_file, all=TRUE)
	df <- merge(x=df, y=params, by.x="parameters", by.y="hash", all.x=TRUE)
	# Loop over games
	for(i in unique(interaction(df$mw_0, df$mw_1, df$mw_2))) {
		d <- subset(df, interaction(df$mw_0, df$mw_1, df$mw_2) == i)
		for(h in unique(d$parameters)) {
			c <- subset(d, d$parameters == h)
			game = sprintf("bias_20/caseload_sqlite/%s-%s", i, as.character(c$game)[1])
			target = directories(game, FALSE, as.character(c$decision_rule_signaller)[1])
			finished = sprintf("%s/finished.png", target)
			referred = sprintf("%s/referred.png", target)	
			do_complete(c, finished, referred)
			do_signals(c, sprintf("%s/%s", target, "signals_%s.png"))
		}
	}
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

complete <- function(df, alspac) {
	target = directories(as.character(df$game)[1], alspac, as.character(df$decision_rule_signaller)[1])
	finished = sprintf("%s/finished.png", target)
	referred = sprintf("%s/referred.png", target)
	do_complete(df, finished, referred)
}

do_complete <- function(df, finished, referred) {
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
	do_signals(df, target)
}

do_signals <- function(df, target) {
	for(i in 0:2) {
		print(sprintf("Writing %s", sprintf(target, i)))
		png(sprintf(target, i))
		print(signals_by_type(df, i))
		dev.off()
	}
}