require(ggplot2)
source("methods.R")

figures <- function(signaller, responder, file, name, dir, target_dir) {

df_recognition = read.csv(sprintf("../%s/%s_women.csv", dir, file), all=TRUE)
df_recognition = subset(df_recognition, df_recognition$decision_rule_signaller == signaller)
df_recognition = subset(df_recognition, df_recognition$decision_rule_responder == responder)
df_recognition_c = subset(df_recognition, df_recognition$caseload == 'True')
df_recognition = subset(df_recognition, df_recognition$caseload == 'False')

png(sprintf("../figures/%s/%s/%s_signals_imply_referral_0.png", target_dir, name, file))
print(signals_imply_referral_by_type(df_recognition, 0))
dev.off()

png(sprintf("../figures/%s/%s/%s_signals_imply_referral_1.png", target_dir, name, file))
print(signals_imply_referral_by_type(df_recognition, 1))
dev.off()

png(sprintf("../figures/%s/%s/%s_signals_imply_referral_2.png", target_dir, name, file))
print(signals_imply_referral_by_type(df_recognition, 2))
dev.off()

png(sprintf("../figures/%s/%s/%s_c_signals_imply_referral_0.png", target_dir, name, file))
print(signals_imply_referral_by_type(df_recognition_c, 0))
dev.off()

png(sprintf("../figures/%s/%s/%s_c_signals_imply_referral_1.png", target_dir, name, file))
print(signals_imply_referral_by_type(df_recognition_c, 1))
dev.off()

png(sprintf("../figures/%s/%s/%s_c_signals_imply_referral_2.png", target_dir, name, file))
print(signals_imply_referral_by_type(df_recognition_c, 2))
dev.off()

png(sprintf("../figures/%s/%s/%s_signals_0.png", target_dir, name, file))
print(signals_by_type(df_recognition, 0))
dev.off()

png(sprintf("../figures/%s/%s/%s_signals_1.png", target_dir, name, file))
print(signals_by_type(df_recognition, 1))
dev.off()

png(sprintf("../figures/%s/%s/%s_signals_2.png", target_dir, name, file))
print(signals_by_type(df_recognition, 2))
dev.off()

png(sprintf("../figures/%s/%s/%s_c_signals_0.png", target_dir, name, file))
print(signals_by_type(df_recognition_c, 0))
dev.off()

png(sprintf("../figures/%s/%s/%s_c_signals_1.png", target_dir, name, file))
print(signals_by_type(df_recognition_c, 1))
dev.off()

png(sprintf("../figures/%s/%s/%s_c_signals_2.png", target_dir, name, file))
print(signals_by_type(df_recognition_c, 2))
dev.off()

png(sprintf("../figures/%s/%s/%s_c_finished_by_type.png", target_dir, name, file))
print(finished_by_type(df_recognition_c))
dev.off()
png(sprintf("../figures/%s/%s/%s_finished_by_type.png", target_dir, name, file))
print(finished_by_type(df_recognition))
dev.off()

png(sprintf("../figures/%s/%s/%s_c_referred_by_type.png", target_dir, name, file))
print(referred_by_type(df_recognition_c))
dev.off()
png(sprintf("../figures/%s/%s/%s_referred_by_type.png", target_dir, name, file))
print(referred_by_type(df_recognition))
dev.off()

# Distributions

png(sprintf("../figures/%s/%s/%s_distributions.png", target_dir, name, file))
print(distributions(df_recognition))
dev.off()

png(sprintf("../figures/%s/%s/%s_c_distributions.png", target_dir, name, file))
print(distributions(df_recognition_c))
dev.off()

}