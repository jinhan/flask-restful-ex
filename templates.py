# variabls: election type, party, region, candidate

text_templates = {
	# 작업용 텍스트
	1: '선거 뉴스 For You /n #{custom1} #{custom2} #{custom3}',

	2: '2018년 6월 13일 오전 7시부터 제7대 전국동시지방선거가 막을 열었다. 오후 6시를 기준으로 투표가 마감되었고, 최종 집계된 투표율은 {toorate_avg_nat}%로 나타났다.',

	# 3: '이번 지방선거의 투표율은 지난 선거에 비해 {지난선거최종투표율 - 최종투표율}%p {높은|낮은} 것으로, {선거에 대한 높은 관심을 반영하고 있다|지난 지방선거에 미치지 못했다}. 전국에서 가장 투표율이 높은 지역은 {최종투표율.시도.순위1}이며, 그 뒤를 {최종투표율.시도.순위2}, {최종투표율.시도.순위3}, {최종투표율.시도.순위4}, {최종투표율.시도.순위5}이 뒤따르고 있다.',

	4: '{region1} 지역 전체의 투표율은 {toorate_region1}%로 전국 평균보다 약 {toorate_region1_toorate_avg_nat}% 포인트 {toorate_compare1} 수치이며, {region2}는 {toorate_region2}%로 전국 평균보다 약간 {toorate_compare2} 투표율을 보였다.',

	5: '{hour}시 현재 전국 평균 개표율은 {openrate_avg_nat}%이며, 서울은 {openrate_seoul}%, 경기도는 {openrate_gyeonggi}%의 개표 진행 상황을 보이고 있다.',

	# 6: '{현재 시간.시각} 현재 전국 선거구에서의 개표는 이전 선거 동일 시간보다 {빠른|느린} 속도로 진행되고 있다. 따라서 이전 선거에 비해 {이른|늦은} 시간에 선거 결과가 나타날 것으로 보인다.',

	7: '{hour}시 현재 {region1} 지역 전체의 개표율은 {openrate_region1}%로 전국 평균보다 약 {openrate_region1_openrate_avg_nat}% 포인트 {openrate_compare1} 수치이며, {region2}는 {openrate_region2}%로 전국 평균보다 {compare_region2} 개표율을 보였다. 전국에서 가장 개표가 빠른 지역은 {openrate_sido_rank1}이며, {region1}지역에서 개표가 가장 빠른 곳은 {openrate_region1_rank1_name}로 {openrate_region1_rank1}%의 개표율을 보이고 있다.',

	8: '{hour}시 현재 총 000개의 지방자치단체장 및 지방자치 의원을 선출하는 이번 지방 선거에서 {rank1_party}은 {rank1_party_num}개의 선거구에서 1위를 달리고 있다. 그 뒤를 {rank2_party}({rank2_party_num}), {rank3_party}({rank3_party_num}){이|가} 잇고 있다.',

	9: '{hour}시 현재 전국 00개의 {election_type} 선거에서 {rank1_party}은 {rank1_party_num}개의 선거구에서 1위를 달리고 있다. 그 뒤를 {rank2_party}({rank2_party_num}), {rank3_party}({rank3_party_num}){이|가} 잇고 있다.',

	10: '{hour}시 현재 {region1} {election_type} 선거에서는 {openrate_region1}%의 개표율을 보이는 가운데 {region1_rank1_party} {region1_rank1_candidate} 후보가 {pollrate_region1_rank1}%의 득표율로 1위, {region1_rank2_party} {region1_rank2_candidate}} 후보가 {pollrate_region1_rank2}%의 득표율로 2위를 달리고 있다.',

	11: '{hour} 현재 {region2} {election_type2} 선거에서는 {openrate_region2}%의 개표율을 보이는 가운데 {region2_rank1_party} {region2_rank1_candidate} 후보가 {pollrate_region2_rank1}%의 득표율로 1위, {region2_rank2_party} {region2_rank2_candidate} 후보가 {pollrate_region2_rank2}%의 득표율로 2위를 달리고 있다.',
}


# img_templates = {
# 	1: { # headline
# 		'type':1, # var
# 		'bgColor',
# 	},
# 	2: { # mayor
# 		'bg':'background.png', # var
# 		'bg_eff': '', # var
# 		'text_font':'NanumBarunGothic.otf',
# 		'text_color':'black',
# 		'text_size':'large',
# 		'text_align':'center',
# 		'text_pos':'mid',
# 	},
# 	3: { # mayor
# 		'bg':'background.png', # var
# 		'bg_eff': '', # var
# 		'text_font':'NanumBarunGothic.otf',
# 		'text_color':'black',
# 		'text_size':'large',
# 		'text_align':'center',
# 		'text_pos':'mid',
# 	},
# 	4: { # mayor
# 		'bg':'background.png', # var
# 		'bg_eff': '', # var
# 		'text_font':'NanumBarunGothic.otf',
# 		'text_color':'black',
# 		'text_size':'large',
# 		'text_align':'center',
# 		'text_pos':'mid',
# 	},
# 	5: { # mayor
# 		'bg':'background.png', # var
# 		'bg_eff': '', # var
# 		'text_font':'NanumBarunGothic.otf',
# 		'text_color':'black',
# 		'text_size':'large',
# 		'text_align':'center',
# 		'text_pos':'mid',
# 	},
# 	6: { # mayor
# 		'bg':'background.png', # var
# 		'bg_eff': '', # var
# 		'text_font':'NanumBarunGothic.otf',
# 		'text_color':'black',
# 		'text_size':'large',
# 		'text_align':'center',
# 		'text_pos':'mid',
# 	},
# 	7: { # mayor
# 		'bg':'background.png', # var
# 		'bg_eff': '', # var
# 		'text_font':'NanumBarunGothic.otf',
# 		'text_color':'black',
# 		'text_size':'large',
# 		'text_align':'center',
# 		'text_pos':'mid',
# 	},
# }


# party2bg = {
# 	'더불어민주당':'blue.png',
# 	'자유한국당':'red.png',
# 	'바른미래당':'mint.png',
# 	None: 'default',
# }
