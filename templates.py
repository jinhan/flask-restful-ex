# variabls: election type, party, region, candidate

text_templates = {
	# headline
	1: '{hour} 현재 득표율입니다.',
	# mayor: 시간, 선거명, 개표율, 정당 후보, 득표율, 정당 후보, 득표율
	2: '{hour}시 현재 {elec} 선거에서는 {open}%의 개표율을 보이는 가운데 {rank1} 후보가 {poll1}%의 득표율로 1위, {rank2} 후보가 {poll2}%의 득표율로 2위를 달리고 있다.',
}


img_templates = {
	1: { # headline
		'bg':'background.png', # var
		'bg_eff': '', # var
		'text_font':'NanumBarunGothic.otf',
		'text_color':'black',
		'text_size':'large',
		'text_align':'center',
		'text_pos':'mid',
	},
	2: { # mayor
		'bg':'background.png', # var
		'bg_eff': '', # var
		'text_font':'NanumBarunGothic.otf',
		'text_color':'black',
		'text_size':'large',
		'text_align':'center',
		'text_pos':'mid',
	},
}


party2bg = {
	'더불어민주당':'blue.png',
	'자유한국당':'red.png',
	'바른미래당':'mint.png',
}
