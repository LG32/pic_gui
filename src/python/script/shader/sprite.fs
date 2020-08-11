#version 330 core
out vec4 FragColor;

in vec2 TexCoord;

// texture samplers
uniform sampler2D texture;
uniform vec4 multiColor;
uniform vec4 additiveColor;

void main()
{
	// linearly interpolate between both textures (80% container, 20% awesomeface)
	vec4 color = texture(texture, TexCoord);
	color.xyz = multiColor.xyz * color.xyz;
	FragColor = color;

	vec4 _tex_map_ = texture(texture, TexCoord);
    vec4 _col_add_multi_;
    _col_add_multi_.xyz = _tex_map_.xyz * multiColor.xyz;
    _col_add_multi_.w = _tex_map_.w;
	_col_add_multi_ *= multiColor.w;
    _col_add_multi_.xyz += additiveColor.xyz * _tex_map_.w * multiColor.w;
    _col_add_multi_.xyz += additiveColor.w * _col_add_multi_.xyz;
	FragColor = _col_add_multi_;
}