import random
import string


def random_name_generator(N):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))


def img_directory_path_input_target(instance, filename):
    ext = filename.split('.')[-1]
    key = random_name_generator(6)
    filename = "%s.%s" % (key, ext)
    return 'acgpn/inputs/T{}_{}'.format(instance.id, filename)


def img_directory_path_input_human(instance, filename):
    ext = filename.split('.')[-1]
    key = random_name_generator(6)
    filename = "%s.%s" % (key, ext)
    return 'acgpn/inputs/H{}_{}'.format(instance.id, filename)


def img_directory_path_input_avatar(instance, filename):
    ext = filename.split('.')[-1]
    key = random_name_generator(6)
    filename = "%s.%s" % (key, ext)
    return 'acgpn/inputs/A{}_{}'.format(instance.id, filename)



def img_directory_path_acgpn_input_nukki(instance, filename):
    ext = filename.split('.')[-1]
    key = random_name_generator(6)
    filename = "%s.%s" % (key, ext)
    return 'acgpn/encoded/N{}_{}'.format(instance.id, filename)


def img_directory_path_acgpn_input_nukki_mask(instance, filename):
    ext = filename.split('.')[-1]
    key = random_name_generator(6)
    filename = "%s.%s" % (key, ext)
    return 'acgpn/encoded/NM{}_{}'.format(instance.id, filename)


def img_directory_path_acgpn_input_warping_mask(instance, filename):
    ext = filename.split('.')[-1]
    key = random_name_generator(6)
    filename = "%s.%s" % (key, ext)
    return 'acgpn/encoded/WM{}_{}'.format(instance.id, filename)


def img_directory_path_acgpn_input_human_model(instance, filename):
    ext = filename.split('.')[-1]
    key = random_name_generator(6)
    filename = "%s.%s" % (key, ext)
    return 'acgpn/encoded/H{}_{}'.format(instance.id, filename)


def img_directory_path_acgpn_input_human_segment(instance, filename):
    ext = filename.split('.')[-1]
    key = random_name_generator(6)
    filename = "%s.%s" % (key, ext)
    return 'acgpn/encoded/HS{}_{}'.format(instance.id, filename)


def img_directory_path_acgpn_output_image(instance, filename):
    ext = filename.split('.')[-1]
    key = random_name_generator(6)
    filename = "%s.%s" % (key, ext)
    return 'acgpn/output/{}_{}'.format(instance.id, filename)
