library(sqldf)

my.pwd = '~/RouteRobot/cluster/'

# copied data here after running /scraping/driver.py
d <- read.csv("~/RouteRobot/cluster/climb.csv", row.names=1, stringsAsFactors=FALSE)

# good analysis starts with a good schema
climb = data.frame(
  href = as.character(d$href),
  nickname = as.character(d$nickname),
  is_route = as.logical(d$is_route),
  is_area = as.logical(d$is_area),
  feet = as.numeric(d$feet),
  page_views = as.numeric(d$page_views),
  pitches = as.numeric(d$pitches),
  protect_rate = as.character(d$protect_rate),
  commitment = as.character(d$commitment),
  boulder = as.logical(d$boulder),
  sport = as.logical(d$sport),
  trad = as.logical(d$trad),
  tr = as.logical(d$tr),
  aid = as.logical(d$aid),
  alpine = as.logical(d$alpine),
  chipped = as.logical(d$chipped),
  ice = as.logical(d$ice),
  mixed = as.logical(d$mixed),
  grade = as.numeric(d$grade),
  rateHueco = as.character(d$rateHueco),
  rateYDS = as.character(d$rateYDS),
  rateFloatHueco = as.numeric(d$rateFloatHueco),
  ratePCTHueco = as.numeric(d$ratePCTHueco),
  rateFloatYDS = as.numeric(d$rateFloatYDS),
  ratePCTYDS = as.numeric(d$ratePCTYDS),
  staraverage = as.numeric(d$staraverage),
  starvotes = as.numeric(d$starvotes),
  name = as.character(d$name),
  elevation = as.character(d$elevation),
  season = as.character(d$season),
  fa = as.character(d$fa)
)

source(paste0(my.pwd,'viz.R'))
print(YDS_histogram(climb))
print(Hueco_histogram(climb))