import logging

from OpenGL.GL import shaders, glUniform1fv, glGetUniformLocation, GL_VERTEX_SHADER, GL_FRAGMENT_SHADER

# from OpenGL.raw.GL.VERSION.GL_2_0 import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER

_log = logging.getLogger(__name__)

DEBUG = True


class ShaderProgram(object):

    def __init__(self, name=None, vertex_shader_src=None, fragment_shader_src=None, uniforms=None):
        self._name = name
        self._vertex_shader_src = vertex_shader_src
        self._fragment_shader_src = fragment_shader_src
        self._program = 0
        self.uniformData = {}

        ## parse extra options from the shader definition
        if uniforms is not None:
            for k, v in uniforms.items():
                self.uniformData[k] = v

    def compile(self):
        try:
            if self._vertex_shader_src and self._fragment_shader_src:
                vertex_shader = shaders.compileShader(self._vertex_shader_src, GL_VERTEX_SHADER)
                fragment_shader = shaders.compileShader(self._fragment_shader_src, GL_FRAGMENT_SHADER)
                self._program = shaders.compileProgram(vertex_shader, fragment_shader)
        except Exception as ex:
            _log.error("Failed to compile vertex/fragment shader.", ex)
            self._program = 0

            if DEBUG:
                raise

    @property
    def name(self):
        return self._name

    @property
    def program(self):
        return self._program

    def __enter__(self):
        shaders.glUseProgram(self.program)  # lgtm [py/call/wrong-arguments]

        try:
            ## load uniform values into program
            for uniformName, data in self.uniformData.items():
                loc = self.uniform(uniformName)
                if loc == -1:
                    raise Exception('Could not find uniform variable "%s"' % uniformName)

                glUniform1fv(loc, len(data), data)
        except:
            shaders.glUseProgram(0)
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        shaders.glUseProgram(0)

    def uniform(self, name):
        """Return the location integer for a uniform variable in this program"""
        return glGetUniformLocation(self.program, name.encode('utf_8'))


class ShaderRegistry(object):
    """ Global states and settings, shared as a borg object. """

    __shared_state = None

    __default_shader = {
        "balloon": ShaderProgram("balloon",
                                 """
                                 varying vec3 normal;
                                 void main() {
                                    // compute here for use in fragment shader
                                    normal = normalize(gl_NormalMatrix * gl_Normal);
                                    gl_FrontColor = gl_Color;
                                    gl_BackColor = gl_Color;
                                    gl_Position = ftransform();
                                 }
                                 """,
                                 """
                                 varying vec3 normal;
                                 void main() {
                                    vec4 color = gl_Color;
                                    color.w = min(color.w + 2.0 * color.w * pow(normal.x*normal.x + normal.y*normal.y, 5.0), 1.0);
                                    gl_FragColor = color;
                                 }
                                 """),

        "shaded": ShaderProgram("shaded",
                                """
                     varying vec3 normal;
                void main() {
                    // compute here for use in fragment shader
                    normal = normalize(gl_NormalMatrix * gl_Normal);
                    gl_FrontColor = gl_Color;
                    gl_BackColor = gl_Color;
                    gl_Position = ftransform();
                }               
                                """,
                                """
                                 varying vec3 normal;
                void main() {
                    vec4 color = gl_Color;
                    float s = pow(normal.x*normal.x + normal.y*normal.y, 2.0);
                    color.x = color.x + s * (1.0-color.x);
                    color.y = color.y + s * (1.0-color.y);
                    color.z = color.z + s * (1.0-color.z);
                    gl_FragColor = color;
                }  
                                """),

        "heightColor": ShaderProgram("heightColor",
                                     """
                                      varying vec4 pos;
                       void main() {
                           gl_FrontColor = gl_Color;
                           gl_BackColor = gl_Color;
                           pos = gl_Vertex;
                           gl_Position = ftransform();
                       }
                                     """,
                                     """
                                      uniform float colorMap[9];
                       varying vec4 pos;
                       //out vec4 gl_FragColor;   // only needed for later glsl versions
                       //in vec4 gl_Color;
                       void main() {
                           vec4 color = gl_Color;
                           color.x = colorMap[0] * (pos.z + colorMap[1]);
                           if (colorMap[2] != 1.0)
                               color.x = pow(color.x, colorMap[2]);
                           color.x = color.x < 0. ? 0. : (color.x > 1. ? 1. : color.x);
                           
                           color.y = colorMap[3] * (pos.z + colorMap[4]);
                           if (colorMap[5] != 1.0)
                               color.y = pow(color.y, colorMap[5]);
                           color.y = color.y < 0. ? 0. : (color.y > 1. ? 1. : color.y);
                           
                           color.z = colorMap[6] * (pos.z + colorMap[7]);
                           if (colorMap[8] != 1.0)
                               color.z = pow(color.z, colorMap[8]);
                           color.z = color.z < 0. ? 0. : (color.z > 1. ? 1. : color.z);
                           
                           color.w = 1.0;
                           gl_FragColor = color;
                       }
                                     """, uniforms={'colorMap': [
                1, 1, 1,
                1, 0.5, 1,
                1, 0, 1]}),

        "edge_highlight": ShaderProgram("edge_highlight",
                                        """
           varying vec3 normal;
                        void main() {
                            // compute here for use in fragment shader
                            normal = normalize(gl_NormalMatrix * gl_Normal);
                            gl_FrontColor = gl_Color;
                            gl_BackColor = gl_Color;
                            gl_Position = ftransform();
                        }
                                        """,
                                        """
          varying vec3 normal;
                        void main() {
                            vec4 color = gl_Color;
                            float s = pow(normal.x*normal.x + normal.y*normal.y, 2.0);
                            color.x = color.x + s * (1.0-color.x);
                            color.y = color.y + s * (1.0-color.y);
                            color.z = color.z + s * (1.0-color.z);
                            gl_FragColor = color;
                        }
                                        """),

        "directional_lighting": ShaderProgram("directional_lighting",
                                              """
                                             void main()
             {
                 vec3 normal, lightDir, viewVector, halfVector;
                 vec4 diffuse, ambient, globalAmbient, specular = vec4(0.0);
                 float NdotL,NdotHV;
                 
                 /* first transform the normal into eye space and normalize the result */
                 normal = normalize(gl_NormalMatrix * gl_Normal);
                 
                 /* now normalize the light's direction. Note that according to the
                 OpenGL specification, the light is stored in eye space. Also since 
                 we're talking about a directional light, the position field is actually 
                 direction */
                 lightDir = normalize(vec3(gl_LightSource[0].position));
                 
                 /* compute the cos of the angle between the normal and lights direction. 
                 The light is directional so the direction is constant for every vertex.
                 Since these two are normalized the cosine is the dot product. We also 
                 need to clamp the result to the [0,1] range. */
                 
                 NdotL = max(dot(normal, lightDir), 0.0);
                 
                 /* Compute the diffuse, ambient and globalAmbient terms */
                 diffuse = gl_FrontMaterial.diffuse * gl_LightSource[0].diffuse;
                 ambient = gl_FrontMaterial.ambient * gl_LightSource[0].ambient;
                 globalAmbient = gl_LightModel.ambient * gl_FrontMaterial.ambient;
                 
                 /* compute the specular term if NdotL is  larger than zero */
                 if (NdotL > 0.0) {
             
                     NdotHV = max(dot(normal, normalize(gl_LightSource[0].halfVector.xyz)),0.0);
                     specular = gl_FrontMaterial.specular * gl_LightSource[0].specular * pow(NdotHV,gl_FrontMaterial.shininess);
                 }
                 
                 gl_FrontColor = globalAmbient + NdotL * diffuse + ambient + specular;
                 
                 gl_Position = ftransform();
                 
                 
                 
                 
                 
             }  
                                              """,
                                              """
                                               void main()
             {
                 gl_FragColor = gl_Color;
             }
                                              """),
    }

    def __init__(self):
        """ Constructor. """
        if not ShaderRegistry.__shared_state:
            ShaderRegistry.__shared_state = self.__dict__

            self.__registry = {None: ShaderProgram()}
        else:
            self.__dict__ = ShaderRegistry.__shared_state

    def add(self, shader):
        if isinstance(shader, ShaderProgram):
            if shader.name in self.__registry:
                # Already in
                return

            shader.compile()
            self.__registry[shader.name] = shader
        elif isinstance(shader, str):
            if shader in self.__registry:
                # Already in
                return

            if shader in self.__default_shader:
                shader_prog = self.__default_shader[shader]
                shader_prog.compile()
                self.__registry[shader_prog.name] = shader_prog

    def __getitem__(self, item):
        return self.__registry[item]
