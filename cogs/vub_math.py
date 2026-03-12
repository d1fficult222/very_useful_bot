import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice, Range
import random, math
from typing import Optional
import math_module as m
import settings
from lang import *

class Math(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_unload(self):
        self.bot.remove_command("correlation")
        self.bot.remove_command("simfrac")
        self.bot.remove_command("factorize")
        self.bot.remove_command("solve21")
        self.bot.remove_command("solve31")
        self.bot.remove_command("rand")
        self.bot.remove_command("dice")
        self.bot.remove_command("vector")
        self.bot.remove_command("vectorl")
        self.bot.remove_command("surface")
        self.bot.remove_command("average")
        self.bot.remove_command("det3")
        self.bot.remove_command("det2")
        self.bot.remove_command("invrmtx2")
        self.bot.remove_command("p")
        self.bot.remove_command("c")
        self.bot.remove_command("common_deg_to_rad")
    
    # --- Command: simfrac ---
    @app_commands.command(name="simfrac", description=text("cmd.simfrac.description"))
    @app_commands.describe(a=text("cmd.simfrac.a"), b=text("cmd.simfrac.b"))
    async def simfrac(self, interaction: discord.Interaction, a: int, b: int):
        frac: m.Fraction = m.Fraction(a,b)
        frac.simplify()
        if frac.b == 1:
            t = text("cmd.simfrac.result1",frac.a)
        else:
            t = text("cmd.simfrac.result2",frac.a,frac.b)
        embed = discord.Embed(
            title=t,
            description=text("cmd.simfrac.origional",a,b),
            color=settings.Colors.math
        )
        embed.add_field(name=text("cmd.simfrac.float"), value=frac.to_float(), inline=True)
        embed.add_field(name=text("cmd.simfrac.percentage"), value=f"{frac.to_percentage()}%", inline=True)
        await interaction.response.send_message(embed=embed)


    # --- Command: factorize ---
    @app_commands.command(name="factorize", description=text("cmd.factorize.description"))
    @app_commands.describe(n=text("cmd.factorize.n"))
    async def factorize(self, interaction: discord.Interaction, n: int):
        x = m.factorize(n)
        x.sort()
        t = text("cmd.factorize.is_prime",n) if len(x) == 1 else x
        embed = discord.Embed(
            title=text("cmd.factorize.result",n),
            description=t,
            color=settings.Colors.math
        )
        await interaction.response.send_message(embed=embed)


    # --- Command: solve21 ---
    @app_commands.command(name="solve21", description=text("cmd.solve21.description"))
    @app_commands.describe(eq1=text("cmd.solve21.eq1"), eq2=text("cmd.solve21.eq2"))
    async def solve21(self, interaction: discord.Interaction, eq1:str, eq2: str):
        try:
            s = m.solve_21(eq1, eq2)
            d = ""
            t = text("cmd.solve21.one_sol")
            for key, value in s.items():
                if type(value) == bool:
                    if value == False:
                        t = text("cmd.solve21.no_sol")
                        break
                    if value == True:
                        t = text("cmd.solve21.inf_sol")
                        break
                else:
                    if type(value) == m.Fraction:
                        value = f"{value.a}/{value.b}"
                    d += f"{key}={value}\n"
            embed = discord.Embed(
                title=t,
                description=d,
                color=settings.Colors.math
            )
            embed.add_field(name=text("cmd.solve21.eq1"),value=eq1,inline=True)
            embed.add_field(name=text("cmd.solve21.eq2"),value=eq2,inline=True)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title=text("cmd.solve21.err"),
                description=text("cmd.solve21.err"),
                color=settings.Colors.fail
            )
            embed.add_field(name=text("cmd.solve21.eq1"),value=eq1,inline=True)
            embed.add_field(name=text("cmd.solve21.eq2"),value=eq2,inline=True)
            embed.add_field(name=text("cmd.solve21.err"),value=e)
            await interaction.response.send_message(embed=embed, ephemeral=True)


    # --- Command: solve31 ---
    @app_commands.command(name="solve31", description=text("cmd.solve31.description"))
    @app_commands.describe(eq1=text("cmd.solve31.eq1"), eq2=text("cmd.solve31.eq2"), eq3=text("cmd.solve31.eq3"))
    async def solve31(self, interaction: discord.Interaction, eq1:str, eq2: str, eq3: str):
        try:
            s = m.solve_31(eq1, eq2, eq3)
            d = ""
            t = text("cmd.solve31.one_sol")
            for key, value in s.items():
                if type(value) == bool:
                    if value == False:
                        t = text("cmd.solve31.no_sol")
                        break
                    if value == True:
                        t = text("cmd.solve31.inf_sol")
                        break
                else:
                    if type(value) == m.Fraction:
                        value = f"{value.a}/{value.b}"
                    d += f"{key}={value}\n"
            embed = discord.Embed(
                title=t,
                description=d,
                color=settings.Colors.math
            )
            embed.add_field(name=text("cmd.solve31.eq1"),value=eq1,inline=True)
            embed.add_field(name=text("cmd.solve31.eq2"),value=eq2,inline=True)
            embed.add_field(name=text("cmd.solve31.eq3"),value=eq3,inline=True)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title=text("cmd.solve31.err"),
                description=text("cmd.solve31.err"),
                color=settings.Colors.fail
            )
            embed.add_field(name=text("cmd.solve31.eq1"),value=eq1,inline=True)
            embed.add_field(name=text("cmd.solve31.eq2"),value=eq2,inline=True)
            embed.add_field(name=text("cmd.solve31.eq3"),value=eq3,inline=True)
            embed.add_field(name=text("cmd.solve31.err"),value=e)
            await interaction.response.send_message(embed=embed, ephemeral=True)


    # --- Command: average ---
    @app_commands.command(name="average", description=text("cmd.average.description"))
    @app_commands.describe(items=text("cmd.average.items"))
    async def average(self, interaction: discord.Interaction, items: str):
        nums = items.split(" ")
        try:
            nums = [float(i) for i in nums]
            result = sum(nums)/len(nums)
            embed=discord.Embed(
                title=text("cmd.average.result",result),
                color=settings.Colors.math
            )
            for i in range(len(nums)):
                embed.add_field(name=text("cmd.average.value",i+1),value=nums[i],inline=True)
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title=text("cmd.average.err"),
                description=e,
                color=settings.Colors.fail
            )
            for i in range(len(nums)):
                embed.add_field(name=text("cmd.average.value",i+1),value=nums[i],inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)


    # --- Command: correlation ---
    @app_commands.command(name="correlation", description=text("cmd.correlation.description"))
    @app_commands.describe(x=text("cmd.correlation.x"), y=text("cmd.correlation.y"))
    async def correlation(self, interaction: discord.Interaction, x: str, y: str):
        xi = x.split(" ")
        yi = y.split(" ")
        if len(xi) != len(yi):
            await interaction.response.send_message("err1")
        
        xi = [int(i) for i in xi]
        yi = [int(i) for i in yi]
        ax = sum(xi) / len(xi)  # average x
        ay = sum(yi) / len(yi)  # average y
        xi_ax = [i - ax for i in xi]  # x離均差
        yi_ay = [i - ay for i in yi]  # y離均差
        xaya = [xi_ax[i] * yi_ay[i] for i in range(len(xi))]  # 上面兩個相乘
        xi_ax_2 = [i * i for i in xi_ax]  # x離均差平方
        yi_ay_2 = [i * i for i in yi_ay]  # y離均差平方

        def is_int(n: float) -> bool:
            return n % 1 == 0

        print(sum(xaya), sum(xi_ax_2), sum(yi_ay_2))

        # r = xaya / (√xi_ax_2 * √yi_ay_2)
        if is_int(sum(xaya)) and is_int(sum(xi_ax_2)) and is_int(sum(yi_ay_2)):
            fa = int(sum(xaya))  # 分子
            fb = m.sim_sqrt(int(sum(xi_ax_2) * sum(yi_ay_2)))  # 分母
            if fb[1] == 1:
                frac = m.Fraction(fa,fb[0])
                frac.simplify()
                r = [frac, 1]
                if r[0].b == 1:
                    des = f"{r[0].a}"
                else:
                    des = f"{r[0].a} / {r[0].b}"
            else:
                frac = m.Fraction(fa,fb[0]*fb[1])
                frac.simplify()
                r = [frac,fb[1]]
                if r[0].b == 1:
                    des = f"{r[0].a} * √{r[1]}"
                else:
                    des = f"{r[0].a} / {r[0].b} * √{r[1]}"
        else:
            des = sum(xaya) / (math.sqrt(sum(xi_ax_2)) * math.sqrt(sum(yi_ay_2)))


        embed = discord.Embed(
            title=text("cmd.correlation.correlation"),
            description=des,
            color=settings.Colors.math
        )
        embed.add_field(name="x", value=tuple(xi))
        embed.add_field(name="y", value=tuple(yi))
        await interaction.response.send_message(embed=embed)


    # --- Command: rand ---
    @app_commands.command(name="rand", description=text("cmd.rand.description"))
    @app_commands.describe(items=text("cmd.rand.items"), amount=text("cmd.rand.amount"))
    async def rand(self, interaction: discord.Interaction, items: str, amount: Optional[int]):
        choices: list = items.split(" ")
        if (not amount and amount != 0) or amount < 0 or amount > len(choices):
            rand_i = random.randint(0,len(choices)-1)
            s = choices[rand_i]
            embed = discord.Embed(
                title=text("cmd.rand.title1",s),
                description=items.replace(" ", ", "),
                color=settings.Colors.math
            )
        else:
            if amount == 0: amount = random.randint(2,len(choices))
            # amount
            for i in range(len(choices)-amount):
                rand_i = random.randint(0,len(choices)-1)
                choices.pop(rand_i)
            # random order
            for i in range(len(choices)):
                i1 = random.randint(0, len(choices)-1)
                i2 = random.randint(0, len(choices)-1)
                choices[i1], choices[i2] = choices[i2], choices[i1]
            s = str(choices).replace('[','').replace(']','').replace("'",'')
            embed = discord.Embed(
                title=text("cmd.rand.title2",amount,s),
                description=items.replace(" ", ", "),
                color=settings.Colors.math
            )  
        await interaction.response.send_message(embed=embed)


    # --- Command: dice ---
    @app_commands.command(name="dice", description=text("cmd.dice.desription"))
    @app_commands.describe(faces=text("cmd.dice.faces"))
    async def dice(self, interaction: discord.Interaction, faces: Optional[int], amount: Optional[int]):
        ran = []
        if faces:  
            if amount:
                ran = random.randint(1,faces)
            else:
                for i in range(amount): ran.append(random.randint(1,faces))
        else:
            if amount:
                ran = random.randint(1,faces)
            else:
                for i in range(amount): ran.append(random.randint(1,6))
        await interaction.response.send_message(str(ran))


    # --- Command: p ---
    @app_commands.command(name="p", description=text("cmd.p.description"))
    @app_commands.describe(n=text("cmd.p.n"), k=text("cmd.p.k"))
    async def p(self, interaction: discord.Interaction, n: Range[int,1,25], k: Range[int,1,25]):
        try:
            result = math.perm(n,k)
        except Exception as e:
            embed = discord.Embed(
                title=text("cmd.p.err"),
                description=e,
                color=settings.Colors.fail
            )
            embed.add_field(name="n",value=n,inline=True)
            embed.add_field(name="k",value=k,inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title=text("cmd.p.title",result),
                description=f"P({n}, {k})",
                color=settings.Colors.math
            )
            await interaction.response.send_message(embed=embed)


    # --- Command: c ---
    @app_commands.command(name="c", description=text("cmd.c.description"))
    @app_commands.describe(n=text("cmd.c.n"), k=text("cmd.c.k"))
    async def c(self, interaction: discord.Interaction, n: Range[int,1,25], k: Range[int,1,25]):
        try:
            result = math.comb(n,k)
        except Exception as e:
            embed = discord.Embed(
                title=text("cmd.c.err"),
                description=e,
                color=settings.Colors.fail
            )
            embed.add_field(name="n",value=n,inline=True)
            embed.add_field(name="k",value=k,inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title=text("cmd.c.title",result),
                description=f"C({n}, {k})",
                color=settings.Colors.math
            )
            await interaction.response.send_message(embed=embed)


    # --- Command: vector ---
    @app_commands.command(name="vector", description=text("cmd.vector.description"))
    @app_commands.describe(
            x0=text("cmd.vector.x0"),
            y0=text("cmd.vector.y0"),
            z0=text("cmd.vector.z0"),
            action=text("cmd.vector.action"),
            x1=text("cmd.vector.x1"),
            y1=text("cmd.vector.y1"),
            z1=text("cmd.vector.z1")
    )
    @app_commands.choices(
            action=[
                    Choice(name=text("cmd.vector.to"), value="to"),
                    Choice(name=text("cmd.vector.dot"), value="dot"),
                    Choice(name=text("cmd.vector.cross"), value="cross")
            ]
    )
    async def vector(
        self, 
        interaction: discord.Interaction,
        x0: int, y0: int, z0: int,
        action: Choice[str],
        x1: int, y1: int, z1: int
    ):
        
        a = (x0, y0, z0)
        b = (x1, y1, z1)
        
        match action.value:
            case "to":
                # 計算向量
                ab = (x1-x0, y1-y0, z1-z0)
                length = m.sim_sqrt(ab[0]*ab[0]+ab[1]*ab[1]+ab[2]*ab[2])
                if length[0] == 1:
                    t = f"{text('cmd.vector.length')}√{length[1]}"
                elif length[1] == 1:
                    t = f"{text('cmd.vector.length')}{length[1]}"
                else:
                    t = f"{text('cmd.vector.length')}{length[0]}√{length[1]}"

                embed = discord.Embed(
                    title=f"AB{text('cmd.vector.vector')} `{ab}`",
                    description=t,
                    color=settings.Colors.math
                )
                embed.add_field(name=f"A{text('cmd.vector.point')}", value=a, inline=True)
                embed.add_field(name=f"B{text('cmd.vector.point')}", value=b, inline=True)
                await interaction.response.send_message(embed=embed)
            case "dot":
                # 內積
                a_dot_b = x0*x1 + y0*y1 + z0*z1
                embed = discord.Embed(
                    title=f"{text('cmd.vector.dot_product')} `{a_dot_b}`",
                    color=settings.Colors.math
                )
                embed.add_field(name=f"A{text('cmd.vector.vector')}", value=a, inline=True)
                embed.add_field(name=f"B{text('cmd.vector.vector')}", value=b, inline=True)
                await interaction.response.send_message(embed=embed)
            case "cross":
                # 外積
                # |y0 z0| |z0 x0| |x0 y0|
                # |y1 z1|,|z1 x1|,|x1 y1|

                o = [
                    y0*z1 - z0*y1,
                    z0*x1 - x0*z1,
                    x0*y1 - y0*x1
                ]
                length = m.sim_sqrt(o[0]*o[0]+o[1]*o[1]+o[2]*o[2])
                if length[0] == 1:
                    t = f"{text('cmd.vector.length')}√{length[1]}"
                elif length[1] == 1:
                    t = f"{text('cmd.vector.length')}{length[1]}"
                else:
                    t = f"{text('cmd.vector.length')}{length[0]}√{length[1]}"

                embed = discord.Embed(
                    title=f"{text('cmd.vector.dot_product')} `({o[0]}, {o[1]}, {o[2]})`",
                    description=t,
                    color=settings.Colors.math
                )
                embed.add_field(name=f"A{text('cmd.vector.vector')}", value=a, inline=True)
                embed.add_field(name=f"B{text('cmd.vector.vector')}", value=b, inline=True)
                await interaction.response.send_message(embed=embed)


    # --- Command: vectorl ---
    @app_commands.command(name="vectorl", description=text("cmd.vectorl.description"))
    @app_commands.describe(x="x",y="y",z="z")
    async def vectorl(self, interaction: discord.Interaction, x: int, y: int, z: int):
            length = m.sim_sqrt(x*x + y*y + z*z)
            if length[0] == 1:
                t = f"{text('cmd.vectorl.length')}√{length[1]}"
            elif length[1] == 1:
                t = f"{text('cmd.vectorl.length')}{length[1]}"
            else:
                t = f"{text('cmd.vectorl.length')}{length[0]}√{length[1]}"

            embed = discord.Embed(
                title=t,
                color=settings.Colors.math
            )
            embed.add_field(name=text("cmd.vectorl.vector"), value=f"({x}, {y}, {z})", inline=True)
            await interaction.response.send_message(embed=embed)  


    # --- Command: surface ---
    @app_commands.command(name="surface", description=text("cmd.surface.description"))
    @app_commands.describe(
        nx=text("cmd.surface.nx"),
        ny=text("cmd.surface.ny"),
        nz=text("cmd.surface.nz"),
        x=text("cmd.surface.x"),
        y=text("cmd.surface.y"),
        z=text("cmd.surface.z")
    )
    async def surface(
        self, 
        interaction: discord.Interaction,
        nx: int, ny: int, nz: int,
        x: int, y: int, z: int
    ):
        d = nx*x + ny*y + nz*z
        gcd = math.gcd(nx,ny,nz,d)
        nx //= gcd
        ny //= gcd
        nz //= gcd
        d //= gcd
        surf = f"{nx}x{'+' if ny>0 else ''}{ny}y{'+' if nz>0 else ''}{nz}z={d}"
        embed = discord.Embed(
            title=f"{text('cmd.surface.surface')} `{surf}`",
            color=settings.Colors.math
        )
        embed.add_field(name=text("cmd.surface.n"), value=f"({nx}, {ny}, {nz})", inline=True)
        embed.add_field(name=text("cmd.surface.point"), value=f"({x}, {y}, {z})", inline=True)
        await interaction.response.send_message(embed=embed)


    # --- Command: det3 ---
    @app_commands.command(name="det3", description=text("cmd.det3.description"))
    @app_commands.describe(
        a1=text("cmd.det3.a1"),
        a2=text("cmd.det3.a2"),
        a3=text("cmd.det3.a3"),
        b1=text("cmd.det3.b1"),
        b2=text("cmd.det3.b2"),
        b3=text("cmd.det3.b3"),
        c1=text("cmd.det3.c1"),
        c2=text("cmd.det3.c2"),
        c3=text("cmd.det3.c3"),
    )
    async def det3(
        self, 
        interaction: discord.Interaction,
        a1: int, a2: int, a3: int,
        b1: int, b2: int, b3: int,
        c1: int, c2: int, c3: int
    ):
        # |a1 a2 a3|
        # |b1 b2 b3|
        # |c1 c2 c3|
        result = a1*b2*c3 + a2*b3*c1 + a3*b1*c2 - a3*b2*c1 - a2*b1*c3 - a1*b3*c2
        
        # Format width
        width = max([len(str(i)) for i in [a1,a2,a3,b1,b2,b3,c1,c2,c3]])
        
        embed = discord.Embed(
            title=f"{text('cmd.det3.determinant')} `{result}`",
            description=
            f"`|{a1: {width}d} {a2: {width}d} {a3: {width}d}|`\n`|{b1: {width}d} {b2: {width}d} {b3: {width}d}|`\n`|{c1: {width}d} {c2: {width}d} {c3: {width}d}|`",
            color=settings.Colors.math
        )
        await interaction.response.send_message(embed=embed)


    # --- Command: det2 ---
    @app_commands.command(name="det2", description=text("cmd.det2.description"))
    @app_commands.describe(
        a1=text("cmd.det2.a1"),
        a2=text("cmd.det2.a2"),
        b1=text("cmd.det2.b1"),
        b2=text("cmd.det2.b2"),
    )
    async def det2(
        self, 
        interaction: discord.Interaction,
        a1: int, a2: int,
        b1: int, b2: int,
    ):
        # |a1 a2|
        # |b1 b2|
        result = a1*b2 - a2*b1
        
        # Format width
        width = max([len(str(i)) for i in [a1,a2,b1,b2]])
        
        embed = discord.Embed(
            title=f"{text('cmd.det2.determinant')} `{result}`",
            description=
            f"`|{a1: {width}d} {a2: {width}d}|`\n`|{b1: {width}d} {b2: {width}d}|`",
            color=settings.Colors.math
        )
        await interaction.response.send_message(embed=embed)


    # --- Command: intrmtx2 ---
    @app_commands.command(name="invrmtx2", description=text("cmd.invrmtx2.description"))
    @app_commands.describe(
        a=text("cmd.det2.a1"),
        b=text("cmd.det2.a2"),
        c=text("cmd.det2.b1"),
        d=text("cmd.det2.b2"),
    )
    async def invrmtx2(
        self, 
        interaction: discord.Interaction,
        a: int, b: int,
        c: int, d: int
    ):
        # A = ⌈a b⌉, A^-1 = ⌈d/det(A) -b/det(A)⌉
        #     ⌊c d⌋         ⌊-c/det(A) a/det(A)⌋
        # 
        # det(A) = |a b|, no inverse if det(A)=0
        #          |c d|
        det = a * d - b * c
        has_invr = True if det != 0 else False
        if has_invr:
            a1 = d / det
            b1 = -b / det
            c1 = -c / det
            d1 = a / det
            # fraction
            if type(a1) == float and len(str(a1)) < 6: a1 = str(a1)
            else: t = m.Fraction(d,det); t.simplify; a1 = f"{t.a}/{t.b}" if t.b != 1 else t.a
            if type(b1) == float and len(str(b1)) < 6: b1 = str(b1)
            else: t = m.Fraction(-b,det); t.simplify; b1 = f"{t.a}/{t.b}" if t.b != 1 else t.a
            if type(c1) == float and len(str(c1)) < 6: c1 = str(c1)
            else: t = m.Fraction(-c,det); t.simplify; c1 = f"{t.a}/{t.b}" if t.b != 1 else t.a
            if type(d1) == float and len(str(d1)) < 6: d1 = str(d1)
            else: t = m.Fraction(a,det); t.simplify; d1 = f"{t.a}/{t.b}" if t.b != 1 else t.a


        # Format width
        width = max([len(str(i)) for i in [a,b,c,d]])
        embed = discord.Embed(
            title=text("cmd.invrmtx2.exist") if has_invr else text("cmd.invrmtx2.not_exist"),
            description=
            f"{text('cmd.invrmtx2.origional')}\n `⌈{a: {width}d} {b: {width}d}⌉`\n`⌊{c: {width}d} {d: {width}d}⌋`",
            color=settings.Colors.math
        )
        if has_invr:
            embed.description += f"\n{text('cmd.invrmtx2.inverse')}\n`⌈{a1} {b1}⌉`\n`⌊{c1} {d1}⌋`"
        await interaction.response.send_message(embed=embed)


    # --- Command: common_deg_to_rad ---
    @app_commands.command(name="common_deg_to_rad", description=text("cmd.common_deg_to_rad.description"))
    @app_commands.describe(angle=text("cmd.common_deg_to_rad.angle"))
    @app_commands.choices(
        angle = [Choice(name=f"{i}°", value=i) for i in [15*j for j in range(0,25)]]
    )
    async def common_deg_to_rad(self, interaction: discord.Interaction, angle: Choice[int]):
        # a pi / b
        gcd = math.gcd(angle.value, 180)
        a = angle.value // gcd
        b = 180 // gcd
        result = f"{a if a != 1 else ''}π{'/'+str(b) if b != 1 else ''}"
        await interaction.response.send_message(f"`{angle.value}°` = **`{result}`**")




async def setup(bot: commands.Bot):
    await bot.add_cog(Math(bot))