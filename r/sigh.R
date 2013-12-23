require(ggplot2)
require(sqldf)

num_rounds_type <- function(df, type, x, y, file) {
    df = eval(parse(text=sprintf("subset(df, df$type_%d_finished > 0)", type)))
    #df <- subset(df, filter > 0)
    # Average number of rounds played
    x = eval(parse(text=sprintf("df$%s",x)))
    y = eval(parse(text=sprintf("df$%s",y)))
    fill = eval(parse(text=sprintf("df$rounds_played_type_%d", type)))
    d$x = x
    d$y = y
    d$fill = fill
    #df <- aggregate(df, by=list(x, y), FUN=mean)
    c <- ggplot(d, aes(x=x, y=y))
    png(file)
    print(c + geom_tile(aes(fill=fill)))
    dev.off()
}

payoffs_type <- function(df, type, x, y) {
    # Average payoff accrued
    df = eval(parse(text=sprintf("subset(df, df$type_%d_frequency > 0)", type)))
    #df <- subset(df, filter > 0)
    x = eval(parse(text=sprintf("df$%s",x)))
    y = eval(parse(text=sprintf("df$%s",y)))
    fill = eval(parse(text=sprintf("df$accrued_payoffs_type_%d", type)))
    #df <- aggregate(df, by=list(x, y), FUN=mean)
    c <- ggplot(df, aes(x=x, y=y))
    return(c + geom_tile(aes(fill=fill)))
}

signals_type <- function(df, type, signal, x, y) {
    # Levelplot of average signal frequency across whole game
    # Include only rounds where at least some of that type played
    # Type 0
    df = eval(parse(text=sprintf("subset(df, df$type_%d_frequency > 0)", type)))
    #df <- subset(df, filter > 0)
    # Average payoff accrued
    x = eval(parse(text=sprintf("df$%s",x)))
    y = eval(parse(text=sprintf("df$%s",y)))
    fill = eval(parse(text=sprintf("df$type_%d_signal_%d", type, signal)))
    #df <- aggregate(df, by=list(x, y), FUN=mean)
    c <- ggplot(df, aes(x=x, y=y))
    return(c + geom_tile(aes(fill=fill)))
}

honesty_type <- function(df, type, x, y) {
    # Levelplot of normalised average absolute signal distance.
    # Include only rounds where at least some of that type played
    # Type 0
    df = eval(parse(text=sprintf("subset(df, df$type_%d_frequency > 0)", type)))
    #df <- subset(df, filter > 0)
    # Average payoff accrued
    x = eval(parse(text=sprintf("df$%s",x)))
    y = eval(parse(text=sprintf("df$%s",y)))
    for(signal in 0:2) {
         fill = eval(parse(text=sprintf("df$type_%d_signal_%d", type, signal)))
    }
    #df <- aggregate(df, by=list(x, y), FUN=mean)
    c <- ggplot(df, aes(x=x, y=y))
    return(c + geom_tile(aes(fill=fill)))
}


load <- function(x) {
    df <- sqldf("select * from results", dbname=x)
    params <- sqldf("select * from parameters", dbname=x)
    df <- merge(x=df, y=params, by.x="hash", by.y="hash", all.x=TRUE)
    print(sprintf("Loaded %s", x))
    return(df)
}

num_rounds <- function(df) {
    # Average number of rounds played over time for all types
    # Include only rounds where at least some of that type finished
    # Type 0
    s <- subset(df, df$type_0_finished > 0)
    d$appointment <- s['appointment']
    d$num_rounds <- s['rounds_played_type_0']
    d$player_type <- "Light"
    # Type 1
    s <- subset(df, df$type_1_finished > 0)
    e$appointment <- s['appointment']
    e$num_rounds <- s['rounds_played_type_1']
    e$player_type <- "Moderate"
    d <- rbind(d, e)
    # Type 2
    s <- subset(df, df$type_2_finished > 0)
    e$appointment <- s['appointment']
    e$num_rounds <- s['rounds_played_type_2']
    e$player_type <- "Heavy"
    d <- rbind(d, e)
    
    c <- ggplot(d, aes(x=appointment, y=num_rounds, color=player_type)) + xlab("Appointment") + ylab("Rounds played")
    c <- c + stat_summary(fun.data = "mean_cl_boot", geom="smooth", aes(group=player_type))   +  theme(text = element_text(family='CMU Serif',size=15)) + scale_colour_discrete(name = "Type")
    return(c)
}

signals_by_type <- function(df, type) {
    # Include only rounds where at least some of that type played
    # Type 0
    df = eval(parse(text=sprintf("subset(df, df$type_%d_frequency > 0)", type)))
    #df <- subset(df, filter > 0)
    frame_type = paste(paste("df$type", type, sep="_"), "signal", sep="_")
    a = paste(frame_type, 0, sep="_")
    b = paste(frame_type, 1, sep="_")
    c = paste(frame_type, 2, sep="_")
    d$appointment <- s['appointment']
    d$num_rounds <- s[a]
    d$player_type <- "Light"
    # Type 1
    s <- subset(df, df$type_1_finished > 0)
    e$appointment <- s['appointment']
    e$num_rounds <- s[b]
    e$player_type <- "Moderate"
    d <- rbind(d, e)
    # Type 2
    s <- subset(df, df$type_2_finished > 0)
    e$appointment <- s['appointment']
    e$num_rounds <- s[c]
    e$player_type <- "Heavy"
    d <- rbind(d, e)
    
    c <- ggplot(d, aes(x=appointment, y=num_rounds, color=player_type)) + xlab("Appointment") + ylab("Signal frequency")
    c <- c + stat_summary(fun.data = "mean_cl_boot", geom="smooth", aes(group=player_type))   +  theme(text = element_text(family='CMU Serif',size=15)) + scale_colour_discrete(name = "Signal")
    return(c)
}

load <- function(x) {
    df <- sqldf("select * from results where appointment > 500", dbname=x)
    params <- sqldf("select * from parameters", dbname=x)
    df <- merge(x=df, y=params, by.x="hash", by.y="hash", all.x=TRUE)
    print(sprintf("Loaded %s", x))
    return(df)
}

files = c("/Users/jg1g12/Downloads/1_women_proportions_women.db", "/Users/jg1g12/Downloads/2_women_proportions_women.db", "/Users/jg1g12/Downloads/3_women_proportions_women.db")
for(x in files) {
    df <- load(x)
    ##df <- aggregate(df, by=list(df$women_1, df$women_2, df$game, df$decision_rule_signaller, df$decision_rule_responder, df$player_type), FUN=mean)
    #df$accrued_payoffs = (df$accrued_payoffs - min(df$accrued_payoffs)) / (max(df$accrued_payoffs) - min(df$accrued_payoffs))
    print("Merged.")
    for(i in unique(df$game)) {
            d <- subset(df, df$game == i)

            for(j in 0:2) {
                png(sprintf("../figures/women_proportions_num_rounds_%s_%s_type_%d_women.png", as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                c = num_rounds_type(d, j, "women_1", "women_2")
                print(c)
                dev.off()
                png(sprintf("../figures/women_proportions_payoffs_%s_%s_type_%d_women.png", as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                c = payoffs_type(d, j, "women_1", "women_2")
                print(c)
                dev.off()
                for(k in 0:2) {
                    png(sprintf("../figures/women_proportions_signal_%d_%s_%s_type_%d_women.png", k, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                    c = signals_type(d, j, "women_1", "women_2")
                    print(c)
                    dev.off()
                }
            }
            rm(d)
    }
    print("Made figures.")
    rm(df)
}

files = c("/Users/jg1g12/Downloads/1_mw_proportions_women.db", "/Users/jg1g12/Downloads/2_mw_proportions_women.db", "/Users/jg1g12/Downloads/3_mw_proportions_women.db", "/Users/jg1g12/Downloads/4_mw_proportions_women.db", "/Users/jg1g12/Downloads/5_mw_proportions_women.db", "/Users/jg1g12/Downloads/6_mw_proportions_women.db")
for(x in files) {
    df <- load(x)
    ##df <- aggregate(df, by=list(df$women_1, df$women_2, df$game, df$decision_rule_signaller, df$decision_rule_responder, df$player_type), FUN=mean)
    #df$accrued_payoffs = (df$accrued_payoffs - min(df$accrued_payoffs)) / (max(df$accrued_payoffs) - min(df$accrued_payoffs))
    print("Merged.")
    for(i in unique(df$game)) {
            d <- subset(df, df$game == i)
            dir = "../figures"
            if(d$women_0 > 0.8) {
                dir = sprintf("%s/alspac", dir)
            }

            for(j in 0:2) {
                file = sprintf("%s/mw_proportions_num_rounds_%s_%s_type_%d_women.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j)
                png()
                c = num_rounds_type(d, j, "mw_1", "mw_2")
                print(c)
                dev.off()
                png(sprintf("%s/mw_proportions_payoffs_%s_%s_type_%d_women.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                c = payoffs_type(d, j, "mw_1", "mw_2")
                print(c)
                dev.off()
                for(k in 0:2) {
                    png(sprintf("%s/mw_proportions_signal_%d_%s_%s_type_%d_women.png", dir, k, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                    c = signals_type(d, j, "mw_1", "mw_2")
                    print(c)
                    dev.off()
                }
            }
            rm(d)
    }
    print("Made figures.")
    rm(df)
}

files = c("/Users/jg1g12/Downloads/1_mw_sharing_women.db", "/Users/jg1g12/Downloads/2_mw_sharing_women.db", "/Users/jg1g12/Downloads/3_mw_sharing_women.db", "/Users/jg1g12/Downloads/4_mw_sharing_women.db", "/Users/jg1g12/Downloads/5_mw_sharing_women.db", "/Users/jg1g12/Downloads/6_mw_sharing_women.db")
for(x in files) {
    df <- load(x)
    ##df <- aggregate(df, by=list(df$women_1, df$women_2, df$game, df$decision_rule_signaller, df$decision_rule_responder, df$player_type), FUN=mean)
    #df$accrued_payoffs = (df$accrued_payoffs - min(df$accrued_payoffs)) / (max(df$accrued_payoffs) - min(df$accrued_payoffs))
    print("Merged.")
    for(i in unique(df$game)) {
            d <- subset(df, df$game == i)
            dir = "../figures"
            if(d$women_0 > 0.8) {
                dir = sprintf("%s/alspac", dir)
            }

            for(j in 0:2) {
                png(sprintf("%s/mw_sharing_num_rounds_%s_%s_type_%d_women.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                c = num_rounds_type(d, j, "mw_share_width", "mw_share_bias")
                print(c)
                dev.off()
                png(sprintf("%s/mw_sharing_payoffs_%s_%s_type_%d_women.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                c = payoffs_type(d, j, "mw_share_width", "mw_share_bias")
                print(c)
                dev.off()
                for(k in 0:2) {
                    png(sprintf("%s/mw_sharing_signal_%d_%s_%s_type_%d_women.png", dir, k, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                    c = signals_type(d, j, "mw_share_width", "mw_share_bias")
                    print(c)
                    dev.off()
                }
            }
            rm(d)
    }
    print("Made figures.")
    rm(df)
}

files = c("/Users/jg1g12/Downloads/1_women_sharing_women.db", "/Users/jg1g12/Downloads/2_women_sharing_women.db", "/Users/jg1g12/Downloads/3_women_sharing_women.db", "/Users/jg1g12/Downloads/4_women_sharing_women.db", "/Users/jg1g12/Downloads/5_women_sharing_women.db", "/Users/jg1g12/Downloads/6_women_sharing_women.db")
for(x in files) {
    df <- load(x)
    ##df <- aggregate(df, by=list(df$women_1, df$women_2, df$game, df$decision_rule_signaller, df$decision_rule_responder, df$player_type), FUN=mean)
    #df$accrued_payoffs = (df$accrued_payoffs - min(df$accrued_payoffs)) / (max(df$accrued_payoffs) - min(df$accrued_payoffs))
    print("Merged.")
    for(i in unique(df$game)) {
            d <- subset(df, df$game == i)
            dir = "../figures"
            if(d$women_0 > 0.8) {
                dir = sprintf("%s/alspac", dir)
            }

            for(j in 0:2) {
                png(sprintf("%s/women_sharing_num_rounds_%s_%s_type_%d_women.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                c = num_rounds_type(d, j, "women_share_width", "women_share_bias")
                print(c)
                dev.off()
                png(sprintf("%s/women_sharing_payoffs_%s_%s_type_%d_women.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                c = payoffs_type(d, j, "women_share_width", "women_share_bias")
                print(c)
                dev.off()
                for(k in 0:2) {
                    png(sprintf("%s/women_sharing_signal_%d_%s_%s_type_%d_women.png", dir, k, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                    c = signals_type(d, j, "women_share_width", "women_share_bias")
                    print(c)
                    dev.off()
                }
            }
            rm(d)
    }
    print("Made figures.")
    rm(df)
}